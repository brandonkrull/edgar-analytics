#! /usr/bin/env python
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

