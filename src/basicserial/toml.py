#
# Copyright (c) 2018, Jason Simeone
#

import datetime
import decimal
import enum
import fractions
import uuid

from collections import (
    OrderedDict,
    UserDict,
    UserList,
    UserString,
)

from .util import convert_datetimes, get_implementation


SUPPORTED_PACKAGES = ('pytoml', 'toml', 'qtoml', 'tomlkit')


def _make_toml_friendly(value):  # noqa: too-many-return-statements
    if isinstance(value, tuple) and hasattr(value, '_fields'):
        return _make_toml_friendly(value._asdict())

    if isinstance(value, (dict, UserDict)):
        return OrderedDict([
            (key, _make_toml_friendly(value[key]))
            for key in value
        ])

    if isinstance(value, (set, frozenset, tuple, UserList)):
        return [
            _make_toml_friendly(element)
            for element in value
        ]

    if isinstance(value, decimal.Decimal):
        return float(value)

    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()

    if isinstance(value, (UserString, complex, fractions.Fraction, uuid.UUID)):
        return str(value)

    if isinstance(value, enum.Enum):
        return value.value

    return value


def to_toml(value, pretty=False, pkg=None):  # noqa: unused-argument
    """
    Serializes the given value to TOML.

    :param value: the value to serialize
    :param pretty:
        this argument is ignored, as no TOML packages support this type of
        operation
    :type pretty: bool
    :param pkg:
        the TOML package to use for serialization; if not specified, uses the
        first supported package found in the environment
    :type pkg: str
    :rtype: str
    """

    return get_implementation(
        'TOML',
        SUPPORTED_PACKAGES,
        pkg,
    ).dumps(_make_toml_friendly(value)).rstrip()


def from_toml(value, native_datetimes=True, pkg=None):
    """
    Deserializes the given value from TOML.

    :param value: the value to deserialize
    :type value: str
    :param native_datetimes:
        whether or not strings that look like dates/times should be
        automatically cast to the native objects, or left as strings; if not
        specified, defaults to ``True``
    :type native_datetimes: bool
    :param pkg:
        the TOML package to use for deserialization; if not specified, uses the
        first supported package found in the environment
    :type pkg: str
    """

    result = get_implementation(
        'TOML',
        SUPPORTED_PACKAGES,
        pkg,
    ).loads(value)

    if native_datetimes:
        result = convert_datetimes(result)

    return result

