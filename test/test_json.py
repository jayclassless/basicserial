from .common import *

from basicserial import to_json, from_json, SUPPORTED_JSON_PACKAGES


SIMPLE_TYPES = pkg_parameterize(
    SUPPORTED_JSON_PACKAGES,
    (
        (123, '123'),
        (123.45, '123.45'),
        ('foo', '"foo"'),
        (UserString('foo'), '"foo"'),
        (False, 'false'),
        (None, 'null'),
        (complex(123, 45), '"(123+45j)"'),
        (Decimal('123.45'), '123.45'),
        (Fraction(1, 3), '"1/3"'),
        (date(2018, 5, 22), '"2018-05-22"'),
        (time(12, 34, 56), '"12:34:56"'),
        (time(12, 34, 56, 789), '"12:34:56.000789"'),
        (time(12, 34, 56, 789000), '"12:34:56.789000"'),
        (datetime(2018, 5, 22, 12, 34, 56), '"2018-05-22T12:34:56Z"'),
        (datetime(2018, 5, 22, 12, 34, 56, tzinfo=TZ_EST), '"2018-05-22T12:34:56-04:56"'),
        (datetime(2018, 5, 22, 12, 34, 56, 789), '"2018-05-22T12:34:56.000789Z"'),
        (datetime(2018, 5, 22, 12, 34, 56, 789000), '"2018-05-22T12:34:56.789000Z"'),
        (datetime(2018, 5, 22, 12, 34, 56, 789000, tzinfo=TZ_EST), '"2018-05-22T12:34:56.789000-04:56"'),
        (CustomEnum.an_int, '1'),
        (CustomEnum.a_str, '"foo"'),
        (CustomEnum.a_bool, 'false'),
        (SOME_UUID, f'"{str(SOME_UUID)}"'),
    ),
)

@pytest.mark.parametrize('pkg,value,expected', SIMPLE_TYPES)
def test_simple_types(pkg, value, expected):
    if pkg == 'ujson':
        expected = expected.replace('/', '\\/')
    assert to_json(value, pkg=pkg) == expected


@pytest.mark.parametrize('pkg', SUPPORTED_JSON_PACKAGES)
def test_unknown_type(pkg):
    with pytest.raises(Exception):
        to_json(object(), pkg=pkg)


SEQUENCE_TYPES = pkg_parameterize(
    SUPPORTED_JSON_PACKAGES,
    (
        ([123, 'foo', True], None),
        ((123, 'foo', True), None),
        (CustomUserList([123, 'foo', True]), None),
        (set([123, 'foo', True]), None),
        (frozenset([123, 'foo', True]), None),
    ),
)

@pytest.mark.parametrize('pkg,value,expected', SEQUENCE_TYPES)
def test_sequence_types(pkg, value, expected):
    out = to_json(value, pkg=pkg)
    assert out.startswith('[')
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

DICT_TYPES = pkg_parameterize(
    SUPPORTED_JSON_PACKAGES,
    (
        ({'foo': 123}, '{"foo":123}'),
        (od, '{"foo":123,"zzz":true,"bar":"foo"}'),
        (CustomNamedTuple(123), '{"foo":123}'),
        (CustomUserDict({'foo': 123}), '{"foo":123}'),
        (dd, '{"foo":123}'),
    ),
)

@pytest.mark.parametrize('pkg,value,expected', DICT_TYPES)
def test_dict_types(pkg, value, expected):
    assert to_json(value, pkg=pkg).replace(" ", "") == expected


@pytest.mark.parametrize('pkg', SUPPORTED_JSON_PACKAGES)
def test_pretty(pkg):
    if pkg == 'hyperjson':
        # hyperjson doesn't make pretties
        return

    assert to_json([1,2,3], pretty=True, pkg=pkg) == """[
  1,
  2,
  3
]"""

    assert to_json(OrderedDict((('foo', 'bar'), ('baz', [1,2]))), pretty=True, pkg=pkg) == """{
  "foo": "bar",
  "baz": [
    1,
    2
  ]
}"""


ALL_TYPES = """{
    "null": null,
    "int": 123,
    "float": 12.34,
    "str": "foo",
    "bool": true,
    "date": "2018-05-22",
    "date_bad": "2018-05-99",
    "time": "12:34:56",
    "time_us": "12:34:56.000789",
    "time_bad": "12:34:99",
    "datetime": "2018-05-22T12:34:56",
    "datetime_utc": "2018-05-22T12:34:56Z",
    "datetime_tz": "2018-05-22T12:34:56-04:56",
    "datetime_fs": "2018-05-22T12:34:56.000789",
    "datetime_fs_tz": "2018-05-22T12:34:56.000789-04:56",
    "datetime_bad": "2018-05-22T12:34:99",
    "list": [
        null,
        123,
        12.34,
        "foo",
        true,
        "2018-05-22",
        "12:34:56",
        "12:34:56.000789",
        "2018-05-22T12:34:56",
        "2018-05-22T12:34:56Z",
        "2018-05-22T12:34:56-04:56",
        "2018-05-22T12:34:56.000789",
        "2018-05-22T12:34:56.000789-04:56"
    ]
}"""


@pytest.mark.parametrize('pkg', SUPPORTED_JSON_PACKAGES)
def test_parse(pkg):
    parsed = from_json(ALL_TYPES, pkg=pkg)
    assert parsed['null'] is None
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
        None,
        123,
        12.34,
        'foo',
        True,
        date(2018, 5, 22),
        time(12, 34, 56),
        time(12, 34, 56, 789),
        datetime(2018, 5, 22, 12, 34, 56),
        datetime(2018, 5, 22, 12, 34, 56, tzinfo=TZ_UTC),
        datetime(2018, 5, 22, 12, 34, 56, tzinfo=TZ_EST),
        datetime(2018, 5, 22, 12, 34, 56, 789),
        datetime(2018, 5, 22, 12, 34, 56, 789, tzinfo=TZ_EST),
    ]

    assert from_json('"2018-05-22"', pkg=pkg) == date(2018, 5, 22)


@pytest.mark.parametrize('pkg', SUPPORTED_JSON_PACKAGES)
def test_parse_no_datetime(pkg):
    parsed = from_json(ALL_TYPES, native_datetimes=False, pkg=pkg)
    assert parsed['null'] is None
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
        None,
        123,
        12.34,
        'foo',
        True,
        "2018-05-22",
        "12:34:56",
        "12:34:56.000789",
        "2018-05-22T12:34:56",
        "2018-05-22T12:34:56Z",
        "2018-05-22T12:34:56-04:56",
        "2018-05-22T12:34:56.000789",
        "2018-05-22T12:34:56.000789-04:56",
    ]

    assert from_json('"2018-05-22"', native_datetimes=False, pkg=pkg) == '2018-05-22'

