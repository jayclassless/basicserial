#
# Copyright (c) 2018, Jason Simeone
#

import datetime
import re

from collections import OrderedDict
from importlib import import_module

import iso8601


_IMPLEMENTATIONS = {}


class Implementation:
    module_name = None

    def __init__(self):
        self._module = None
        if self.module_name:
            try:
                self._module = import_module(self.module_name)
            except ImportError:
                pass

    def is_available(self):
        return self._module is not None

    def serialize(self, value, pretty=False):
        raise NotImplementedError()

    def deserialize(self, value, native_datetimes=True):
        raise NotImplementedError()


class ImplementationRegistry:
    def __init__(self):
        self.implementations = OrderedDict()

    @property
    def registered_packages(self):
        return tuple(self.implementations.keys())

    @property
    def available_packages(self):
        return tuple(
            k
            for k, v in self.implementations.items()
            if v.is_available()
        )

    def register(self, package, clazz):
        self.implementations[package] = clazz()

    def get(self, package=None):
        if package:
            impl = self.implementations.get(package)
            if not impl:
                raise ValueError(
                    '"%s" is not a supported package' % (package,)
                )

            if not impl.is_available():
                raise ValueError(
                    'The "%s" package is not currently available' % (package,)
                )

            return impl

        for impl in self.implementations.values():
            if impl.is_available():
                return impl

        raise NotImplementedError(
            'No supported package available'
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

