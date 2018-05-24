from src.processor import get_inactivity_value, get_value_indices, \
    get_raw_log_data, process_logs


def test_inactivity_value():
    fname = 'tests/input/inactivity_period.txt'

    try:
        inactivity_period = get_inactivity_value(fname)
    except ValueError:
        assert False
    else:
        assert inactivity_period == 2


def test_inactivity_value_bad():
    fname = 'tests/input/inactivity_period_bad.txt'

    try:
        inactivity_period = get_inactivity_value(fname)
    except ValueError:
        assert True


def test_make_raw_data():
    expected = {
        'ip': '107.23.85.jfd',
        'date': '2017-06-30',
        'time': '00:00:00'
    }

    fname = 'tests/input/log.csv'

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
    output_file = 'tests/output/sessionization.txt'
    raw_data = get_raw_log_data('tests/input/log.csv')
    inactivity_period = 'tests/input/inactivity_period.txt'

    with open('tests/output/ref.txt') as f:
        expected = f.readlines()

    with open(output_file, 'a') as f:
        process_logs(raw_data, inactivity_period, f)

    with open(output_file) as f:
        results = f.readlines()

    assert len(results) == len(expected), 'Incorrect number of result items'

    for i, r in enumerate(results):
        expected_split = expected[i].split(',')
        r_split = r.split(',')
        for j, piece in enumerate(r_split):
            assert piece == expected_split[j], \
                'Incorrect value for piece {}'.format(j)
