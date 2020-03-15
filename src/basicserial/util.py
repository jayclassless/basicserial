#
# Copyright (c) 2018, Jason Simeone
#

import datetime
import re

from collections import OrderedDict
from functools import lru_cache
from importlib import import_module

import iso8601


_IMPLEMENTATIONS = {}


@lru_cache()
def get_implementation(scope, supported, pkg):
    if scope not in _IMPLEMENTATIONS:
        _IMPLEMENTATIONS[scope] = OrderedDict()
        for impl in supported:
            try:
                _IMPLEMENTATIONS[scope][impl] = import_module(impl)
            except ImportError:
                _IMPLEMENTATIONS[scope][impl] = None

    if pkg:
        if pkg in _IMPLEMENTATIONS[scope]:
            impl = _IMPLEMENTATIONS[scope][pkg]
            if impl:
                return impl
            raise ValueError(
                'The "%s" library is not currently available' % (pkg,)
            )
        raise ValueError(
            '"%s" is not a supported %s library' % (pkg, scope)
        )

    for impl in _IMPLEMENTATIONS[scope].values():
        if impl:
            return impl

    raise NotImplementedError(
        'No supported %s library available' % (scope,)
    )


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

