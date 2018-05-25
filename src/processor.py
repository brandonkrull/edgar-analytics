from collections import deque
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from os import remove


class User(object):
    """
    User class that is uniquely identified by the anonymized IP address

    A User's session depends on whether the User already has an active session
    or not.

    __repr__ is defined explicitly in order to check of a User is 'in' a list of Users
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
    Session class that is attached to a User. A Session's attributes
    are the necessary attrs for keeping track of a User's activity.
    """

    def __init__(self, start, sleep, count=1):
        self.start = start
        self.end = start
        self.updated = None
        self.sleep = sleep
        self.count = count

    def __str__(self):
        return 'Start: {}, Updated: {}, End: {}, Count: {}'.format(
            self.start, self.updated, self.end, self.count)

    def close(self, ip, output_handle):
        length = relativedelta(self.end, self.start).seconds - self.sleep
        dt_open = self._format_dt_for_output(self.start)
        dt_close = self._format_dt_for_output(self.end, end=True)

        output_line = '{},{},{},{},{}\n'.format(ip, dt_open, dt_close, length,
                                                self.count)
        # print 'Closing ' + output_line
        output_handle.write(output_line)

    def _format_dt_for_output(self, dt, end=False):

        if end:
            out = ' '.join((dt + relativedelta(
                seconds=-self.sleep-1)).isoformat().split('T'))
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
    def _get_session_from_deque(user, open_sessions):
        for u in open_sessions:
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
                # print '----New Record----'
                user = User(record['ip'])
                now = parse(record['date'] + ' ' + record['time'])
                # print "It is now {}".format(now)

                # deal with current user and whether or not they have an open session
                if user not in open_sessions:
                    # print 'Adding user {} to open_sessions'.format(user.ip)
                    user.sess = Session(start=now, sleep=self.inactivity_time)
                    open_sessions.append(user)
                else:
                    sess = self._get_session_from_deque(user, open_sessions)

                    elapsed = sess._compute_session_elapsed(now)
                    if elapsed > self.inactivity_time:
                        # the amount of time this session has elapsed means
                        # the previously opened session should be closed
                        # and a new session started

                        # print 'User {} had open session, but it should be closed and replaced'.format(user.ip)
                        sess.end = now
                        sess.close(user.ip, output_file)
                        open_sessions.remove(user)

                        sess = Session(start=now, sleep=self.inactivity_time)
                    else:
                        sess.updated = now
                        sess.count += 1

                        # print 'User: {} has been updated to {}'.format(user.ip, sess)

                # if time has passed, deal with all remaining open sessions
                clock_elapsed = relativedelta(now, prev).seconds
                # print "time elapsed: {}".format(clock_elapsed)
                if clock_elapsed > 0:
                    number_of_open_sess = len(open_sessions)
                    # print "Checking {} other open sessions".format(number_of_open_sess)

                    for i in range(number_of_open_sess):
                        u = open_sessions.popleft()
                        u.sess.end = now
                        start_time = u.sess.start

                        elapsed = u.sess._compute_session_elapsed(now)
                        # print u.ip + ' ' + str(u.sess)

                        # print 'elapsed: {}, sleep: {}'.format(elapsed, self.inactivity_time)
                        if elapsed > self.inactivity_time:
                            # print 'Closing {}'.format(u.ip)
                            u.sess.end = now
                            u.sess.close(u.ip, output_file)
                        else:
                            open_sessions.append(u)

                        # all subsequent entries should have start times
                        # that are later and need not be iterated through
                        # so simply rotate my deck to put the oldest at the top
                        if relativedelta(now, start_time).seconds < self.inactivity_time:
                            open_sessions.rotate(number_of_open_sess - i + 1)
                            break

                prev = now

                # print '\n'
            else:
                # print 'File closed, proceeding to close remaining sessions'
                # print 'Now is {}'.format(now)
                # print open_sessions

                """
                Once end of the log is reached, close all remaining open sessions
                """

                while open_sessions:
                    u = open_sessions.popleft()
                    # print u.ip + ' ' + str(u.sess)

                    elapsed = u.sess._compute_session_elapsed(now)
                    # print u.ip + ' elapsed {} '.format(elapsed) + str(u.sess)
                    if u.sess.start == now:
                        u.sess.end = now
                    elif u.sess.updated:
                        u.sess.end = u.sess.updated
                    else:
                        u.sess.end = u.sess.start

                    u.sess.end += relativedelta(seconds=self.inactivity_time+1)

                    u.sess.close(u.ip, output_file)


def get_value_indices(keys):
    """
    truth contains the column names that we actually need
    """
    truth = ['ip', 'date', 'time']

    return {k: keys.index(k) for k in keys if k in truth}


def get_raw_log_data(fname):
    data = []
    try:
        with open(fname) as f:
            keys = f.readline().strip().split(',')
            indices = get_value_indices(keys)

            for line in f.readlines():
                list_of_info = line.strip().split(',')
                data.append(
                    {k: list_of_info[v]
                     for k, v in indices.iteritems()})
    except OSError:
        raise OSError('No file {} found'.format(fname))

    return data
