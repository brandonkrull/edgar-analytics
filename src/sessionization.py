#! /usr/bin/env python

from argparse import ArgumentParser
from processor import get_raw_log_data, process_logs

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('log', help='Name of input log file in CSV format')
    parser.add_argument('output', help='Name of output log file in CSV format')
    parser.add_argument(
        'inactivity_period',
        help='Name of file that defines length of inactivity period')

    args = parser.parse_args()

    raw_data = get_raw_log_data(args.log)
    print args.log
    print args.output
    print args.inactivity_period
    with open(args.output, 'w') as handle:
        process_logs(raw_data, args.inactivity_period, handle)

