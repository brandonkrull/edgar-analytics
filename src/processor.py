#! /usr/bin/env python
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


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

