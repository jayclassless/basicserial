from collections import namedtuple, OrderedDict, defaultdict
from datetime import date, time, datetime
from decimal import Decimal
from fractions import Fraction
from pytz import timezone
from six.moves import UserDict, UserList, UserString

import pytest

from basicserial import to_toml, from_toml


class CustomUserDict(UserDict):
    pass

class CustomUserList(UserList):
    pass

class CustomUserString(UserString):
    pass

CustomNamedTuple = namedtuple('CustomNamedTuple', ['foo'])


TZ_EST = timezone('America/New_York')
TZ_UTC = timezone('UTC')

SIMPLE_TYPES = (
    (123, '123'),
    (123.45, '123.45'),
    ('foo', '"foo"'),
    (UserString('foo'), '"foo"'),
    (False, 'false'),
    (complex(123, 45), '"(123+45j)"'),
    (Decimal('123.45'), '123.45'),
    (Fraction(1, 3), '"1/3"'),
    (date(2018, 5, 22), '"2018-05-22"'),
    (time(12, 34, 56), '"12:34:56"'),
    (time(12, 34, 56, 789), '"12:34:56.000789"'),
    (time(12, 34, 56, 789000), '"12:34:56.789000"'),
    (datetime(2018, 5, 22, 12, 34, 56), '"2018-05-22T12:34:56"'),
    (datetime(2018, 5, 22, 12, 34, 56, tzinfo=TZ_EST), '"2018-05-22T12:34:56-04:56"'),
    (datetime(2018, 5, 22, 12, 34, 56, 789), '"2018-05-22T12:34:56.000789"'),
    (datetime(2018, 5, 22, 12, 34, 56, 789000), '"2018-05-22T12:34:56.789000"'),
    (datetime(2018, 5, 22, 12, 34, 56, 789000, tzinfo=TZ_EST), '"2018-05-22T12:34:56.789000-04:56"'),
)

@pytest.mark.parametrize('value,expected', SIMPLE_TYPES)
def test_simple_types(value, expected):
    assert to_toml({'foo': value}) == 'foo = %s' % (expected,)


def test_unknown_type():
    with pytest.raises(Exception):
        to_toml(object())


SEQUENCE_TYPES = (
    ([123, 'foo', True], '[123, "foo", true]'),
    ((123, 'foo', True), '[123, "foo", true]'),
    (CustomUserList([123, 'foo', True]), '[123, "foo", true]'),
)

@pytest.mark.parametrize('value,expected', SEQUENCE_TYPES)
def test_sequence_types(value, expected):
    assert to_toml({'foo': value}) == 'foo = %s' % (expected,)


def test_set_types():
    out = to_toml({'a_set': set([123, 'foo', True])})
    assert out.startswith('a_set = [')
    assert out.endswith(']')
    assert '123' in out
    assert 'true' in out
    assert '"foo"' in out

    out = to_toml({'a_set': frozenset([123, 'foo', True])})
    assert out.startswith('a_set = [')
    assert out.endswith(']')
    assert '123' in out
    assert 'true' in out
    assert '"foo"' in out


od = OrderedDict()
od['foo'] = 123
od['zzz'] = True
od['bar'] = 'foo'

dd = defaultdict(list)
dd['foo'] = 123

DICT_TYPES = (
    ({'foo': 123}, 'foo = 123'),
    (od, 'foo = 123\nzzz = true\nbar = "foo"'),
    (CustomNamedTuple(123), 'foo = 123'),
    (CustomUserDict({'foo': 123}), 'foo = 123'),
    (dd, 'foo = 123'),
)

@pytest.mark.parametrize('value,expected', DICT_TYPES)
def test_dict_types(value, expected):
    assert to_toml(value) == expected


def test_pretty():
    assert to_toml(OrderedDict((('foo', 'bar'), ('baz', [1,2]))), pretty=True) == """foo = "bar"
baz = [1, 2]"""


ALL_TYPES = """
int = 123
float = 12.34
str = 'foo'
bool = true
date = '2018-05-22'
date_bad = '2018-05-99'
time = '12:34:56'
time_us = '12:34:56.000789'
time_bad = '12:34:99'
datetime = '2018-05-22T12:34:56'
datetime_utc = '2018-05-22T12:34:56Z'
datetime_tz = '2018-05-22T12:34:56-04:56'
datetime_fs = '2018-05-22T12:34:56.000789'
datetime_fs_tz = '2018-05-22T12:34:56.000789-04:56'
datetime_bad = '2018-05-22T12:34:99'
list = [
  'foo',
  '2018-05-22',
  '12:34:56',
  '12:34:56.000789',
  '2018-05-22T12:34:56',
  '2018-05-22T12:34:56Z',
  '2018-05-22T12:34:56-04:56',
  '2018-05-22T12:34:56.000789',
  '2018-05-22T12:34:56.000789-04:56',
]"""


def test_parse():
    parsed = from_toml(ALL_TYPES)
    assert parsed['int'] == 123
    assert parsed['float'] == 12.34
    assert parsed['str'] == 'foo'
    assert parsed['bool'] is True
    assert parsed['date'] == date(2018, 5, 22)
    assert parsed['date_bad'] == "2018-05-99"
    assert parsed['time'] == time(12, 34, 56)
    assert parsed['time_us'] == time(12, 34, 56, 789)
    assert parsed['time_bad'] == "12:34:99"
    assert parsed['datetime'] == datetime(2018, 5, 22, 12, 34, 56)
    assert parsed['datetime_utc'] == datetime(2018, 5, 22, 12, 34, 56, tzinfo=TZ_UTC)
    assert parsed['datetime_tz'] == datetime(2018, 5, 22, 12, 34, 56, tzinfo=TZ_EST)
    assert parsed['datetime_fs'] == datetime(2018, 5, 22, 12, 34, 56, 789)
    assert parsed['datetime_fs_tz'] == datetime(2018, 5, 22, 12, 34, 56, 789, tzinfo=TZ_EST)
    assert parsed['datetime_bad'] == "2018-05-22T12:34:99"
    assert parsed['list'] == [
        'foo',
        date(2018, 5, 22),
        time(12, 34, 56),
        time(12, 34, 56, 789),
        datetime(2018, 5, 22, 12, 34, 56),
        datetime(2018, 5, 22, 12, 34, 56, tzinfo=TZ_UTC),
        datetime(2018, 5, 22, 12, 34, 56, tzinfo=TZ_EST),
        datetime(2018, 5, 22, 12, 34, 56, 789),
        datetime(2018, 5, 22, 12, 34, 56, 789, tzinfo=TZ_EST),
    ]


def test_parse_no_datetime():
    parsed = from_toml(ALL_TYPES, native_datetimes=False)
    assert parsed['int'] == 123
    assert parsed['float'] == 12.34
    assert parsed['str'] == 'foo'
    assert parsed['bool'] is True
    assert parsed['date'] == "2018-05-22"
    assert parsed['date_bad'] == "2018-05-99"
    assert parsed['time'] == "12:34:56"
    assert parsed['time_us'] == "12:34:56.000789"
    assert parsed['time_bad'] == "12:34:99"
    assert parsed['datetime'] == "2018-05-22T12:34:56"
    assert parsed['datetime_utc'] == "2018-05-22T12:34:56Z"
    assert parsed['datetime_tz'] == "2018-05-22T12:34:56-04:56"
    assert parsed['datetime_fs'] == "2018-05-22T12:34:56.000789"
    assert parsed['datetime_fs_tz'] == "2018-05-22T12:34:56.000789-04:56"
    assert parsed['datetime_bad'] == "2018-05-22T12:34:99"
    assert parsed['list'] == [
        'foo',
        "2018-05-22",
        "12:34:56",
        "12:34:56.000789",
        "2018-05-22T12:34:56",
        "2018-05-22T12:34:56Z",
        "2018-05-22T12:34:56-04:56",
        "2018-05-22T12:34:56.000789",
        "2018-05-22T12:34:56.000789-04:56",
    ]

