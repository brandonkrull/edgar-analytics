from src.processor import get_value_indices, get_raw_log_data


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
