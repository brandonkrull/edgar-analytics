from src.processor import Processor, get_value_indices, get_raw_log_data


TEST_BASE = 'tests_py/'


def test_inactivity_value():
    inactivity_file_name = TEST_BASE + 'input/inactivity_period.txt'
    output_file = ''

    try:
        proc = Processor(inactivity_file_name, output_file)
    except ValueError:
        assert False
    else:
        assert proc.inactivity_time == 2


def test_inactivity_value_bad_file():
    inactivity_file_name = TEST_BASE + 'input/inactivity_period_verybad.txt'
    output_file = ''

    try:
        Processor(inactivity_file_name, output_file)
    except IOError:
        assert True


def test_inactivity_value_bad():
    inactivity_file_name = TEST_BASE + 'input/inactivity_period_bad.txt'
    output_file = ''

    try:
        Processor(inactivity_file_name, output_file)
    except ValueError:
        assert True


def test_make_raw_data_no_file():
    fname = TEST_BASE + 'input/logger.csv'

    try:
        get_raw_log_data(fname)
    except IOError:
        assert True


def test_make_raw_data():
    expected = {
        'ip': '101.81.133.jja',
        'date': '2017-06-30',
        'time': '00:00:00'
    }

    fname = TEST_BASE + 'input/log.csv'

    data = get_raw_log_data(fname)

    assert data[0] == expected
    assert len(data[0]) == 3


def test_index_constructor():
    expected = [0, 1, 2]
    keys = [
        'ip', 'date', 'time', 'zone', 'cik', 'accession', 'extention', 'code',
        'size', 'idx', 'norefer', 'noagent', 'find', 'crawler', 'browser'
    ]

    indices = get_value_indices(keys)

    assert sum(indices.values()) == sum(expected)


def test_output():
    output_file_name = TEST_BASE + 'output/sessionization.txt'
    raw_data = get_raw_log_data(TEST_BASE + 'input/log.csv')
    inactivity_file_name = TEST_BASE + 'input/inactivity_period.txt'

    proc = Processor(inactivity_file_name, output_file_name)
    proc.process_logs(raw_data)

    with open(output_file_name) as f:
        results = f.readlines()

    with open(TEST_BASE + 'output/ref.txt') as f:
        expected = f.readlines()

    assert len(results) == len(expected), 'Incorrect number of result items'

    for i, r in enumerate(results):
        expected_split = expected[i].split(',')
        r_split = r.split(',')
        for j, piece in enumerate(r_split):
            assert piece == expected_split[j], \
                'Incorrect value for piece {}'.format(j)
