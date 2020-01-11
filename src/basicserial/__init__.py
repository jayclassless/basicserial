#
# Copyright (c) 2018, Jason Simeone
#

import datetime
import decimal
import fractions
import json
import re
import sys

from collections import (
    defaultdict,
    OrderedDict,
    UserDict,
    UserList,
    UserString,
)

import iso8601


__all__ = (
    'to_json',
    'from_json',
    'to_yaml',
    'from_yaml',
    'to_toml',
    'from_toml',
)


try:
    import yaml
except ImportError:
    try:
        import ruamel.yaml as yaml
    except ImportError:
        yaml = None

try:
    import pytoml as toml
except ImportError:
    try:
        import toml
    except ImportError:
        toml = None


class BasicJSONEncoder(json.JSONEncoder):
    SIMPLE_ENCODINGS = (
        (datetime.date, lambda x: x.isoformat()),
        (datetime.time, lambda x: x.isoformat()),
        (decimal.Decimal, float),
        (fractions.Fraction, str),
        (set, list),
        (frozenset, list),
        (complex, str),
        (UserDict, lambda x: x.data),
        (UserList, lambda x: x.data),
        (UserString, lambda x: x.data),
    )

    def default(self, o):  # noqa: method-hidden
        if isinstance(o, datetime.datetime):
            value = o.isoformat()
            if not o.utcoffset():
                value += 'Z'
            return value

        for typ, encoder in self.SIMPLE_ENCODINGS:
            if isinstance(o, typ):
                return encoder(o)

        return super(BasicJSONEncoder, self).default(o)  # pragma: no cover

    def encode(self, o):
        if isinstance(o, tuple) and hasattr(o, '_fields'):
            o = o._asdict()
        return super(BasicJSONEncoder, self).encode(o)


def to_json(value, pretty=False):
    """
    Serializes the given value to JSON.

    :param value: the value to serialize
    :param pretty:
        whether or not to format the output in a more human-readable way; if
        not specified, defaults to ``False``
    :type pretty: bool
    :rtype: str
    """

    options = {
        'sort_keys': False,
        'cls': BasicJSONEncoder,
    }
    if pretty:
        options['indent'] = 2
        options['separators'] = (',', ': ')

    return json.dumps(value, **options)


RE_DATE = re.compile(
    r'^\d{4}-\d{2}-\d{2}$',
)
RE_TIME = re.compile(
    r'^\d{2}:\d{2}:\d{2}(?P<fs>\.\d+)?$',
)
RE_DATETIME = re.compile(
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[-+](\d{2}:\d{2}))?$',
)


def get_date_or_string(value):  # noqa: complex
    if RE_DATETIME.match(value):
        try:
            return iso8601.parse_date(value, default_timezone=None)
        except iso8601.ParseError:
            pass

    if RE_DATE.match(value):
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            pass

    match = RE_TIME.match(value)
    if match:
        if match.groupdict()['fs']:
            fmt = '%H:%M:%S.%f'
        else:
            fmt = '%H:%M:%S'
        try:
            return datetime.datetime.strptime(value, fmt).time()
        except ValueError:
            pass

    return value


def convert_datetimes(value):
    if isinstance(value, list):
        pairs = enumerate(value)
    elif isinstance(value, dict):
        pairs = value.items()

    results = []
    for key, val in pairs:
        if isinstance(val, str):
            val = get_date_or_string(val)

        elif isinstance(val, (dict, list)):
            val = convert_datetimes(val)

        results.append((key, val))

    if isinstance(value, list):
        return [result[1] for result in results]

    return dict(results)


class BasicJsonDecoder:
    def __init__(self, native_datetimes):
        self.native_datetimes = native_datetimes

    def __call__(self, value):
        if self.native_datetimes:
            return convert_datetimes(value)
        return value


def from_json(value, native_datetimes=True):
    """
    Deserializes the given value from JSON.

    :param value: the value to deserialize
    :type value: str
    :param native_datetimes:
        whether or not strings that look like dates/times should be
        automatically cast to the native objects, or left as strings; if not
        specified, defaults to ``True``
    :type native_datetimes: bool
    """

    hook = BasicJsonDecoder(native_datetimes=native_datetimes)
    result = json.loads(value, object_hook=hook)
    if native_datetimes and isinstance(result, str):
        return get_date_or_string(result)
    return result


class BasicYamlDumper(yaml.SafeDumper):  # noqa: too-many-ancestors
    def list_representer(self, data):
        return self.represent_sequence('tag:yaml.org,2002:seq', list(data))

    def dict_representer(self, data):
        return self.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            list(data.items())
        )

    def decimal_representer(self, data):
        return self.represent_scalar('tag:yaml.org,2002:float', str(data))

    def time_representer(self, data):
        return self.represent_scalar('tag:yaml.org,2002:str', data.isoformat())

    def userstring_representer(self, data):
        return self.represent_scalar('tag:yaml.org,2002:str', data.data)

    def complex_representer(self, data):
        return self.represent_scalar('tag:yaml.org,2002:str', str(data))

    def unknown_representer(self, data):
        if isinstance(data, tuple) and hasattr(data, '_fields'):
            return self.dict_representer(data._asdict())
        if isinstance(data, UserDict):
            return self.dict_representer(data)
        if isinstance(data, UserList):
            return self.list_representer(data)
        return self.represent_undefined(data)


YAML_REPRESENTERS = (
    (decimal.Decimal, BasicYamlDumper.decimal_representer),
    (datetime.time, BasicYamlDumper.time_representer),
    (set, BasicYamlDumper.list_representer),
    (frozenset, BasicYamlDumper.list_representer),
    (UserList, BasicYamlDumper.list_representer),
    (defaultdict, BasicYamlDumper.dict_representer),
    (OrderedDict, BasicYamlDumper.dict_representer),
    (UserDict, BasicYamlDumper.dict_representer),
    (UserString, BasicYamlDumper.userstring_representer),
    (complex, BasicYamlDumper.complex_representer),
    (fractions.Fraction, BasicYamlDumper.complex_representer),
    (None, BasicYamlDumper.unknown_representer),
)

for type_, representer in YAML_REPRESENTERS:
    BasicYamlDumper.add_representer(type_, representer)


def to_yaml(value, pretty=False):
    """
    Serializes the given value to YAML.

    :param value: the value to serialize
    :param pretty:
        whether or not to format the output in a more human-readable way; if
        not specified, defaults to ``False``
    :type pretty: bool
    :rtype: str
    """

    if not yaml:
        raise NotImplementedError('No supported YAML library available')

    options = {
        'Dumper': BasicYamlDumper,
        'allow_unicode': True,
    }
    options['default_flow_style'] = not pretty

    return yaml.dump(value, **options).rstrip()


class StringedDatesYamlLoader(yaml.SafeLoader):
    # pylint: disable=too-many-ancestors,no-self-use

    def timestamp_constructor(self, node):
        return node.value


StringedDatesYamlLoader.add_constructor(
    'tag:yaml.org,2002:timestamp',
    StringedDatesYamlLoader.timestamp_constructor,
)


class NativeDatesYamlLoader(yaml.SafeLoader):
    # pylint: disable=too-many-ancestors,no-self-use

    def timestamp_constructor(self, node):
        return get_date_or_string(node.value)

    def str_constructor(self, node):
        return get_date_or_string(node.value)


NativeDatesYamlLoader.add_constructor(
    'tag:yaml.org,2002:str',
    NativeDatesYamlLoader.str_constructor,
)

NativeDatesYamlLoader.add_constructor(
    'tag:yaml.org,2002:timestamp',
    NativeDatesYamlLoader.timestamp_constructor,
)


def from_yaml(value, native_datetimes=True):
    """
    Deserializes the given value from YAML.

    :param value: the value to deserialize
    :type value: str
    :param native_datetimes:
        whether or not strings that look like dates/times should be
        automatically cast to the native objects, or left as strings; if not
        specified, defaults to ``True``
    :type native_datetimes: bool
    """

    if not yaml:
        raise NotImplementedError('No supported YAML library available')

    if native_datetimes:
        loader = NativeDatesYamlLoader
    else:
        loader = StringedDatesYamlLoader

    return yaml.load(value, Loader=loader)


def make_toml_friendly(value):
    if isinstance(value, tuple) and hasattr(value, '_fields'):
        return make_toml_friendly(value._asdict())

    if isinstance(value, dict):
        return OrderedDict([
            (key, make_toml_friendly(value[key]))
            for key in value
        ])

    if isinstance(value, (set, frozenset, tuple, UserList)):
        return [
            make_toml_friendly(element)
            for element in value
        ]

    if isinstance(value, decimal.Decimal):
        return float(value)

    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()

    if isinstance(value, (UserString, complex, fractions.Fraction)):
        return str(value)

    return value


def to_toml(value, pretty=False):  # noqa: unused-argument
    """
    Serializes the given value to TOML.

    :param value: the value to serialize
    :param pretty:
        this argument is ignored, as no TOML libraries support this type of
        operation
    :type pretty: bool
    :rtype: str
    """

    if not toml:
        raise NotImplementedError('No supported TOML library available')

    return toml.dumps(make_toml_friendly(value)).rstrip()


def from_toml(value, native_datetimes=True):
    """
    Deserializes the given value from TOML.

    :param value: the value to deserialize
    :type value: str
    :param native_datetimes:
        whether or not strings that look like dates/times should be
        automatically cast to the native objects, or left as strings; if not
        specified, defaults to ``True``
    :type native_datetimes: bool
    """

    if not toml:
        raise NotImplementedError('No supported TOML library available')

    result = toml.loads(value)

    if native_datetimes:
        result = convert_datetimes(result)

    return result

