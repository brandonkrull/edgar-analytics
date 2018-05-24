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

    def __init__(self, ip, date, time, count=0, length=0, end=0):
        self.ip = ip

        try:
            self.dt = parse(date + ' ' + time)
        except ValueError:
            raise ValueError('Invalid or unknown date/time string')

        self.length = length
        self.count = count
        self.end = end

    def __repr__(self):
        return 'dt: {}, count: {}, length:{}'.format(self.dt, self.count,
                                                     self.length)

    def close(self, output_handle):
        self.end = self.dt + relativedelta(seconds=self.length)
        dt_open = self._format_dt_for_output(self.dt)
        dt_close = self._format_dt_for_output(self.end)

        output_line = '{},{},{},{},{}\n'.format(self.ip, dt_open, dt_close,
                                                self.length, self.count)
        output_handle.write(output_line)

    def _format_dt_for_output(self, dt):
        return ' '.join(dt.isoformat().split('T'))


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
            raise IOError('No such inactivity file {}'.format(inactivity_period_file))

        return inactivity_period

    def process_logs(self, raw_data):
        open_sessions = []
        prev = parse('0366-12-24 23:59:59')

        with open(self.output_file_name, 'a') as output_file:
            for record in raw_data:
                user = User(record['ip'])
                now = parse(record['date'] + ' ' + record['time'])
                elapsed = relativedelta(now, prev).seconds

                if user not in open_sessions:
                    user.sess = Session(count=1, length=0, **record)
                    open_sessions.append(user)
                else:
                    sess = open_sessions[open_sessions.index(user)].sess
                    length = relativedelta(now, sess.dt).seconds - sess.length

                    print "Length of existing session: {}".format(length)
                    if length > self.inactivity_time:
                        sess.close(output_file)
                        open_sessions.remove(user)
                    else:
                        sess.dt = now
                        sess.count += 1

                if elapsed > 0:
                    for u in open_sessions:
                        if u == user:
                            continue

                        length = relativedelta(
                            now, u.sess.dt).seconds - u.sess.length

                        if length > self.inactivity_time:
                            u.sess.length = length
                            sess.close(output_file)
                            open_sessions.remove(u)

                prev = now
            """
            Once the end of the log is reached, close all remaining open sessions
            """
            for u in open_sessions:
                length = relativedelta(now, u.sess.dt).seconds - u.sess.length

                u.sess.length = length
                u.sess.close(output_file)
                open_sessions.remove(u)


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
