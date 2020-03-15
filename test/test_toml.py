from .common import *

from basicserial import to_toml, from_toml, SUPPORTED_TOML_PACKAGES


def q(pkg, value):
    if pkg == 'qtoml':
        if value.startswith('"'):
            return f"'{value[1:-1]}'"
    return value


SIMPLE_TYPES = pkg_parameterize(
    SUPPORTED_TOML_PACKAGES,
    (
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
        (CustomEnum.an_int, '1'),
        (CustomEnum.a_str, '"foo"'),
        (CustomEnum.a_bool, 'false'),
    ),
)

@pytest.mark.parametrize('pkg,value,expected', SIMPLE_TYPES)
def test_simple_types(pkg, value, expected):
    assert to_toml({'foo': value}, pkg=pkg) == 'foo = %s' % (q(pkg, expected),)


@pytest.mark.parametrize('pkg', SUPPORTED_TOML_PACKAGES)
def test_unknown_type(pkg):
    with pytest.raises(Exception):
        to_toml(object(), pkg=pkg)


SEQUENCE_TYPES = pkg_parameterize(
    SUPPORTED_TOML_PACKAGES,
    (
        ([123, 'foo', True], None),
        ((123, 'foo', True), None),
        (CustomUserList([123, 'foo', True]), None),
    ),
)

@pytest.mark.parametrize('pkg,value,expected', SEQUENCE_TYPES)
def test_sequence_types(pkg, value, expected):
    if pkg == 'tomlkit':
        # tomlkit doesn't like sequences with mixed types
        return
    out = to_toml({'foo': value}, pkg=pkg)
    assert out.startswith('foo = [')
    assert out.endswith(']')
    assert '123' in out
    assert 'true' in out
    assert q(pkg, '"foo"') in out


@pytest.mark.parametrize('pkg', SUPPORTED_TOML_PACKAGES)
def test_set_types(pkg):
    if pkg == 'tomlkit':
        # tomlkit doesn't like sequences with mixed types
        return

    out = to_toml({'a_set': set([123, 'foo', True])}, pkg=pkg)
    assert out.startswith('a_set = [')
    assert out.endswith(']')
    assert '123' in out
    assert 'true' in out
    assert q(pkg, '"foo"') in out

    out = to_toml({'a_set': frozenset([123, 'foo', True])}, pkg=pkg)
    assert out.startswith('a_set = [')
    assert out.endswith(']')
    assert '123' in out
    assert 'true' in out
    assert q(pkg, '"foo"') in out


od = OrderedDict()
od['foo'] = 123
dd = defaultdict(list)
dd['foo'] = 123

DICT_TYPES = pkg_parameterize(
    SUPPORTED_TOML_PACKAGES,
    (
        ({'foo': 123}, 'foo = 123'),
        (od, 'foo = 123'),
        (CustomNamedTuple(123), 'foo = 123'),
        (CustomUserDict({'foo': 123}), 'foo = 123'),
        (dd, 'foo = 123'),
    ),
)

@pytest.mark.parametrize('pkg,value,expected', DICT_TYPES)
def test_dict_types(pkg, value, expected):
    assert to_toml(value, pkg=pkg) == expected


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


@pytest.mark.parametrize('pkg', SUPPORTED_TOML_PACKAGES)
def test_parse(pkg):
    parsed = from_toml(ALL_TYPES, pkg=pkg)
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


@pytest.mark.parametrize('pkg', SUPPORTED_TOML_PACKAGES)
def test_parse_no_datetime(pkg):
    parsed = from_toml(ALL_TYPES, native_datetimes=False, pkg=pkg)
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

