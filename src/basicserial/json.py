#
# Copyright (c) 2018, Jason Simeone
#

import datetime
import decimal
import fractions
import enum

from collections import (
    UserDict,
    UserList,
    UserString,
)
from functools import lru_cache

from .util import get_date_or_string, get_implementation, convert_datetimes


SUPPORTED_PACKAGES = ('json', 'simplejson')


@lru_cache()
def _build_encoder(json):
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

        def default(self, o):
            if isinstance(o, datetime.datetime):
                value = o.isoformat()
                if not o.utcoffset():
                    value += 'Z'
                return value

            for typ, encoder in self.SIMPLE_ENCODINGS:
                if isinstance(o, typ):
                    return encoder(o)

            return super().default(o)  # pragma: no cover

        def encode(self, o):
            if isinstance(o, tuple) and hasattr(o, '_fields'):
                o = o._asdict()
            elif isinstance(o, enum.Enum):
                o = o.value
            return super().encode(o)

    return BasicJSONEncoder


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

    options = {
        'sort_keys': False,
        'cls': _build_encoder(json),
    }
    if pretty:
        options['indent'] = 2
        options['separators'] = (',', ': ')

    return json.dumps(value, **options)


class BasicJsonDecoder:
    def __init__(self, native_datetimes):
        self.native_datetimes = native_datetimes

    def __call__(self, value):
        if self.native_datetimes:
            return convert_datetimes(value)
        return value


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

    hook = BasicJsonDecoder(native_datetimes=native_datetimes)
    result = json.loads(value, object_hook=hook)

    if native_datetimes and isinstance(result, str):
        return get_date_or_string(result)

    return result

