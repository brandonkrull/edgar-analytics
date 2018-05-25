from src.processor import Session
from dateutil.parser import parse


record = {'ip': '123.123.123.1', 'date': '0366-12-24', 'time': '23:59:59'}
baddate = {'ip': '123.123.123.1', 'date': '0x66-12-24', 'time': '23:59:59'}
badtime = {'ip': '123.123.123.1', 'date': '0366-12-24', 'time': 'z3:59:59'}


def test_session_init_bad_date():
    try:
        now = parse(baddate['date'] + ' ' + baddate['time'])
        sess = Session(start=now)
    except ValueError:
        assert True
    else:
        assert False


def test_session_init_bad_time():
    try:
        now = parse(badtime['date'] + ' ' + badtime['time'])
        sess = Session(start=now)
    except ValueError:
        assert True
    else:
        assert False


def test_session_init():
    now = parse(record['date'] + ' ' + record['time'])
    sess = Session(start=now, sleep=0)

    assert sess.start == now
    assert sess.end == now
    assert sess.count == 1


def test_date_output_format():
    now = parse(record['date'] + ' ' + record['time'])
    expected = record['date'] + ' ' + record['time']

    sess = Session(start=now, sleep=0)
    output = sess._format_dt_for_output(sess.start)

    assert output == expected
