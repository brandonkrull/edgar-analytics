from src.processor import Session
from dateutil.parser import parse


record = {'ip': '123.123.123.1', 'date': '0366-12-24', 'time': '23:59:59'}
baddate = {'ip': '123.123.123.1', 'date': '0x66-12-24', 'time': '23:59:59'}
badtime = {'ip': '123.123.123.1', 'date': '0366-12-24', 'time': 'z3:59:59'}


def test_session_init_bad_date():
    try:
        sess = Session(**baddate)
    except ValueError as exc:
        assert True
    else:
        assert False


def test_session_init_bad_time():
    try:
        sess = Session(**badtime)
    except ValueError as exc:
        assert True
    else:
        assert False


def test_session_init():
    sess = Session(**record)

    assert sess.ip == '123.123.123.1'
    assert sess.dt == parse(record['date'] + ' ' + record['time'])
    assert sess.length == 0
    assert sess.count == 0
    assert sess.end == 0


def test_date_output_format():
    expected = record['date'] + ' ' + record['time']

    sess = Session(**record)
    output = sess._format_dt_for_output(sess.dt)

    assert output == expected
