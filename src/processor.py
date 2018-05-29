import re
from csv import DictReader, Error
from collections import deque
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from os import remove


class User(object):
    """
    User class that is uniquely identified by the anonymized IP address

    A User's session depends on whether the User already has an active session
    or not.

    attrs:
        self.ip: str       | required
        self.sess: Session | default=None

    methods:
        __repr__ is defined explicitly in order to check of a User is 'in'
    a deque of Users
    """

    def __init__(self, ip, session=None):
        self.ip = ip
        self.sess = session

    def __repr__(self):
        return 'User: {}'.format(self.ip)

    def __eq__(self, other_user):
        """
        This equivalence is based on the assumption in the declaration of
        the problem that IPs are enough to uniquely define a user
        """
        return self.ip == other_user.ip


class Session(object):
    """
    Session class that defines all possible states and is attached to a User.

    attrs:
        self.start: datetime   | start time, never to be updated
        self.updated: datetime | None, until updated, used to check lifetime
        self.end: datetime     | init to start, updated upon Session close

    methods:
        close(ip: str, output_handle: openfile handle 'a') | closes a session
        _format_dt_for_output(dt: datetime) | returns a datetime formatted for output
        _compute_session_elapsed(now: datetime) | computes elapsed time from start to now
    """

    def __init__(self, start, sleep, count=1):
        self.start = start
        self.updated = None
        self.end = start
        self.sleep = sleep
        self.count = count

    def __str__(self):
        return 'Start: {}, Updated: {}, End: {}, Count: {}'.format(
            self.start, self.updated, self.end, self.count)

    def close(self, ip, output_handle):
        """
        Closing a session entails three things:
        1. Computing the length of the session
        2. Formatting the start and end of sessions appropriately
        3. Appending the user's session info to the output file
        """
        length = relativedelta(self.end, self.start).seconds - self.sleep
        dt_open = self._format_dt_for_output(self.start)
        dt_close = self._format_dt_for_output(self.end, end=True)

        output_line = '{},{},{},{},{}\n'.format(ip, dt_open, dt_close, length,
                                                self.count)
        output_handle.write(output_line)

    def _format_dt_for_output(self, dt, end=False):
        """
        Take a datetime.datetime object and convert to str
        in the appropriate format for output

        Note: if end, we need to take away (sleep-1) to account
        for the inclusive nature of the session length definition
        """

        if end:
            out = ' '.join((dt + relativedelta(
                seconds=-self.sleep - 1)).isoformat().split('T'))
        else:
            out = ' '.join(dt.isoformat().split('T'))

        return out

    def _compute_session_elapsed(self, now):
        """ Returns integer number of seconds """
        if self.updated:
            elapsed = relativedelta(now, self.updated).seconds
        else:
            elapsed = relativedelta(now, self.start).seconds

        return elapsed


class Processor(object):
    """
    Processor class is the main workhorse class for log processing

    attrs:
        inactivity_time: int | the amount of time until which a Session should be deemed closed
        output_file_name: str | name of file to append results to

    methods:
        get_inactivity_value(inactivity_period_file: str) | reads from file the sleep time
        _get_session_from_deque(user, deque) | find a user in deque
        process_logs(raw_data: list of dicts)
    """

    def __init__(self, inactivity_time_file, output_file_name):
        self.inactivity_time = self.get_inactivity_value(inactivity_time_file)
        self.output_file_name = output_file_name

        try:
            remove(output_file_name)
        except OSError:
            pass

    @staticmethod
    def get_inactivity_value(inactivity_period_file):
        try:
            with open(inactivity_period_file) as f:
                try:
                    inactivity_period = int(f.readline())
                except ValueError:
                    raise ValueError('invalid inactivity value')
        except IOError:
            raise IOError(
                'No such inactivity file {}'.format(inactivity_period_file))

        return inactivity_period

    @staticmethod
    def _get_session_from_deque(user, deque):
        for u in deque:
            if not u.ip == user.ip:
                continue
            else:
                sess = u.sess
                break

        return sess

    def process_logs(self, raw_data):
        open_sessions = deque()
        prev = parse('0366-12-25 00:00:00')

        with open(self.output_file_name, 'a') as output_file:
            for record in raw_data:
                user = User(record['ip'])
                now = parse(record['date'] + ' ' + record['time'])

                # deal with current user
                # -------------------
                if user not in open_sessions:
                    user.sess = Session(start=now, sleep=self.inactivity_time)
                    open_sessions.append(user)
                else:
                    sess = self._get_session_from_deque(user, open_sessions)

                    elapsed = sess._compute_session_elapsed(now)
                    if elapsed > self.inactivity_time:
                        """
                        since elapsed > inactivity_time
                        the previously opened session should be closed
                        and a new session started
                        """
                        sess.end = now
                        sess.close(user.ip, output_file)
                        open_sessions.remove(user)

                        sess = Session(start=now, sleep=self.inactivity_time)
                    else:
                        sess.updated = now
                        sess.count += 1
                # -------------------

                # if time has passed, deal with all remaining open sessions
                # -------------------
                clock_elapsed = relativedelta(now, prev).seconds
                if clock_elapsed > 0:
                    number_of_open_sess = len(open_sessions)

                    for i in range(number_of_open_sess):
                        u = open_sessions.popleft()
                        u.sess.end = now
                        start_time = u.sess.start

                        elapsed = u.sess._compute_session_elapsed(now)
                        if elapsed > self.inactivity_time:
                            u.sess.end = now
                            u.sess.close(u.ip, output_file)
                        else:
                            open_sessions.append(u)
                        """
                        all subsequent entries should have start times
                        that are later and need not be iterated through
                        so simply rotate my deck to put the oldest at the top
                        """
                        if relativedelta(
                                now,
                                start_time).seconds < self.inactivity_time:
                            open_sessions.rotate(number_of_open_sess - i + 1)
                            break
                # -------------------

                prev = now
            else:
                """
                Once end of the log is reached, close all remaining open sessions
                """

                while open_sessions:
                    u = open_sessions.popleft()

                    if u.sess.start == now:
                        u.sess.end = now
                    elif u.sess.updated:
                        u.sess.end = u.sess.updated
                    else:
                        u.sess.end = u.sess.start

                    u.sess.end += relativedelta(
                        seconds=self.inactivity_time + 1)

                    u.sess.close(u.ip, output_file)


def get_value_indices(keys):
    """
    From a list of keys, find the indices of truth keys
    """
    truth = ['ip', 'date', 'time']
    indices = {}
    for k in truth:
        try:
            indices[k] = keys.index(k)
        except ValueError:
            raise ValueError(
                'There is no "{}" field in the keys'.format(k.upper()))

    return indices


def get_raw_log_data(fname):
    """
    Given a file_name, returns a list of dicts where
    dict = {'ip': ip, 'date': date, 'time': time}
    """
    data = []
    regex = {
        'ip': re.compile(r'[0-9]{3}.[0-9]{1,3}.[0-9]{1,3}.[a-z]{3}'),
        'date': re.compile(r'[0-9]{4}-[0-1][0-9]-[0-3][0-9]'),
        'time': re.compile(r'[0-2]{2}:[0-9]{2}:[0-9]{2}')
    }
    try:
        with open(fname, 'rb') as csvfile:
            csvreader = DictReader(csvfile)

            try:
                for line in csvreader:
                    print line
                    interm = {}
                    for k in ['ip', 'date', 'time']:
                        if regex[k].match(line[k]):
                            interm[k] = line[k]
                        else:
                            break

                    if len(interm) < 3:
                        print 'Incomplete data, skipping line'
                        continue

                    data.append(interm)
            except Error as e:
                print 'Error in file {}, line {}: {}'.format(
                    fname, csvreader.line_num, e)

    except OSError:
        raise OSError('No file {} found'.format(fname))

    return data
