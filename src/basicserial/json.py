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

from .util import (
    get_date_or_string,
    convert_datetimes,
    Implementation,
    ImplementationRegistry,
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


class JsonImplementation(Implementation):
    def serialize(self, value, pretty=False):
        raise NotImplementedError

    def deserialize(self, value, native_datetimes=True):
        result = self._module.loads(value)

        if native_datetimes:
            if isinstance(result, (dict, list)):
                result = convert_datetimes(result)
            elif isinstance(result, str):
                result = get_date_or_string(result)

        return result


class StdlibJsonImplementation(JsonImplementation):
    module_name = 'json'

    def serialize(self, value, pretty=False):
        opts = {
            'sort_keys': False,
        }
        if pretty:
            opts['indent'] = 2
            opts['separators'] = (',', ': ')
        return self._module.dumps(value, **opts)


class SimpleJsonImplementation(StdlibJsonImplementation):
    module_name = 'simplejson'


class OrJsonImplementation(JsonImplementation):
    module_name = 'orjson'

    def _default(self, value):  # noqa: no-self-use
        if isinstance(value, OrderedDict):
            return dict(value)
        raise TypeError

    def serialize(self, value, pretty=False):
        opts = {
            'default': self._default,
        }
        if pretty:
            opts['option'] = self._module.OPT_INDENT_2
        return self._module.dumps(value, **opts).decode('utf-8')


class RapidJsonImplementation(JsonImplementation):
    module_name = 'rapidjson'

    def serialize(self, value, pretty=False):
        opts = {
            'sort_keys': False,
        }
        if pretty:
            opts['indent'] = 2
        return self._module.dumps(value, **opts)


class UJsonImplementation(RapidJsonImplementation):
    module_name = 'ujson'


class HyperJsonImplementation(JsonImplementation):
    module_name = 'hyperjson'

    def serialize(self, value, pretty=False):
        opts = {
            'sort_keys': False,
        }
        return self._module.dumps(value, **opts)


class SimdJsonImplementation(StdlibJsonImplementation):
    module_name = 'simdjson'


IMPLEMENTATIONS = ImplementationRegistry()
IMPLEMENTATIONS.register('json', StdlibJsonImplementation)
IMPLEMENTATIONS.register('simplejson', SimpleJsonImplementation)
IMPLEMENTATIONS.register('orjson', OrJsonImplementation)
IMPLEMENTATIONS.register('rapidjson', RapidJsonImplementation)
IMPLEMENTATIONS.register('ujson', UJsonImplementation)
IMPLEMENTATIONS.register('hyperjson', HyperJsonImplementation)
IMPLEMENTATIONS.register('simdjson', SimdJsonImplementation)


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

    impl = IMPLEMENTATIONS.get(pkg)
    return impl.serialize(_make_json_friendly(value), pretty=pretty)


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

    impl = IMPLEMENTATIONS.get(pkg)
    return impl.deserialize(value, native_datetimes=native_datetimes)
