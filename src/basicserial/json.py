#
# Copyright (c) 2018, Jason Simeone
#

import datetime
import decimal
import fractions
import enum
import uuid

from collections import (
    UserDict,
    UserList,
    UserString,
    OrderedDict,
)

from .util import get_date_or_string, get_implementation, convert_datetimes


SUPPORTED_PACKAGES = (
    'json',
    'simplejson',
    'orjson',
    'rapidjson',
    'ujson',
    'hyperjson',
)


def _encode_datetime(value):
    encoded = value.isoformat()
    if not value.utcoffset():
        encoded += 'Z'
    return encoded


ENCODINGS = (
    (datetime.datetime, _encode_datetime),
    (datetime.date, lambda x: x.isoformat()),
    (datetime.time, lambda x: x.isoformat()),
    (decimal.Decimal, float),
    (fractions.Fraction, str),
    (set, list),
    (frozenset, list),
    (complex, str),
    (UserString, lambda x: x.data),
    (uuid.UUID, str),
)


def _make_json_friendly(value):
    if isinstance(value, tuple) and hasattr(value, '_fields'):
        return _make_json_friendly(value._asdict())

    if isinstance(value, (dict, UserDict)):
        return OrderedDict([
            (key, _make_json_friendly(value[key]))
            for key in value
        ])

    if isinstance(value, (list, set, frozenset, tuple, UserList)):
        return [
            _make_json_friendly(element)
            for element in value
        ]

    if isinstance(value, enum.Enum):
        return value.value

    for typ, encoder in ENCODINGS:
        if isinstance(value, typ):
            return encoder(value)

    return value


def orjson_default(value):
    if isinstance(value, OrderedDict):
        return dict(value)
    raise TypeError


def to_json(value, pretty=False, pkg=None):
    """
    Serializes the given value to JSON.

    :param value: the value to serialize
    :param pretty:
        whether or not to format the output in a more human-readable way; if
        not specified, defaults to ``False``
    :type pretty: bool
    :param pkg:
        the JSON package to use for serialization; if not specified, uses the
        first supported package found in the environment
    :type pkg: str
    :rtype: str
    """

    json = get_implementation(
        'JSON',
        SUPPORTED_PACKAGES,
        pkg,
    )

    options = {}

    if pkg == 'orjson':
        options['default'] = orjson_default
        if pretty:
            options['option'] = json.OPT_INDENT_2
    else:
        options['sort_keys'] = False
        if pretty and pkg not in ('hyperjson',):
            options['indent'] = 2
            if pkg not in ('rapidjson', 'ujson'):
                options['separators'] = (',', ': ')

    encoded = json.dumps(_make_json_friendly(value), **options)
    if pkg == 'orjson':
        encoded = encoded.decode('utf-8')

    return encoded


def from_json(value, native_datetimes=True, pkg=None):
    """
    Deserializes the given value from JSON.

    :param value: the value to deserialize
    :type value: str
    :param native_datetimes:
        whether or not strings that look like dates/times should be
        automatically cast to the native objects, or left as strings; if not
        specified, defaults to ``True``
    :type native_datetimes: bool
    :param pkg:
        the JSON package to use for deserialization; if not specified, uses the
        first supported package found in the environment
    :type pkg: str
    """

    json = get_implementation(
        'JSON',
        SUPPORTED_PACKAGES,
        pkg,
    )

    result = json.loads(value)

    if native_datetimes:
        if isinstance(result, (dict, list)):
            result = convert_datetimes(result)
        elif isinstance(result, str):
            result = get_date_or_string(result)

    return result

