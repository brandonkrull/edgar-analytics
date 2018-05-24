from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


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
        print output_line
        output_handle.write(output_line)

    def _format_dt_for_output(self, dt):
        return ' '.join(dt.isoformat().split('T'))


def get_value_indices(keys):
    """
    truth contains the column names that we actually need
    """
    truth = ['ip', 'date', 'time']

    return {k: keys.index(k) for k in keys if k in truth}


def get_raw_log_data(fname):
    data = []
    with open(fname) as f:
        keys = f.readline().strip().split(',')
        indices = get_value_indices(keys)

        for line in f.readlines():
            list_of_info = line.strip().split(',')
            data.append({k: list_of_info[v] for k, v in indices.iteritems()})

    return data


def process_logs(raw_data, inactivity_time, output_handle):
    open_sessions = []
    for record in raw_data:
        user = User(record['ip'])
        print user
        now = parse(record['date'] + ' ' + record['time'])

        if user not in open_sessions:
            user.sess = Session(count=1, length=0, **record)
            open_sessions.append(user)
            #             print 'adding new user: {}'.format(user.ip)
            #             print user.session
        else:
            sess = open_sessions[open_sessions.index(user)].sess
            length = relativedelta(now, sess.dt).seconds - sess.length

            print "Length of existing session: {}".format(length)
            if length > inactivity_time:
                sess.close(output_handle)
                open_sessions.remove(user)
            else:
                sess.dt = now
                sess.count += 1

        for u in open_sessions:
            if u == user: continue

            length = relativedelta(now, u.sess.dt).seconds - u.sess.length

            if length > inactivity_time:
                u.sess.length = length
                sess.close(output_handle)
                open_sessions.remove(u)
    """
    Once the end of the log is reached, close all remaining open sessions
    """
    for u in open_sessions:
        length = relativedelta(now, u.sess.dt).seconds - u.sess.length

        u.sess.length = length
        u.sess.close(output_handle)
        open_sessions.remove(u)
