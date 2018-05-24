from argparse import ArgumentParser
from processor import get_inactivity_value, get_raw_log_data, process_logs

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('log', help='Name of input log file in CSV format')
    parser.add_argument(
        'inactivity_period_file',
        help='Name of file that defines length of inactivity period')
    parser.add_argument('output', help='Name of output log file in CSV format')

    args = parser.parse_args()

    raw_data = get_raw_log_data(args.log)
    print args.log
    print args.output
    print args.inactivity_period_file

    inactivity_value = get_inactivity_value(args.inactivity_period_file)

    with open(args.output, 'a') as output_file:
        process_logs(raw_data, inactivity_period, output_file)
