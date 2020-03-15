#
# Copyright (c) 2018, Jason Simeone
#

import datetime
import decimal
import enum
import fractions
import uuid

from collections import (
    defaultdict,
    OrderedDict,
    UserDict,
    UserList,
    UserString,
)
from functools import lru_cache

from .util import get_date_or_string, get_implementation


SUPPORTED_PACKAGES = ('yaml', 'ruamel.yaml')


@lru_cache()
def _build_dumper(yaml):  # noqa: complex
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
            return self.represent_scalar(
                'tag:yaml.org,2002:str',
                data.isoformat(),
            )

        def userstring_representer(self, data):
            return self.represent_scalar('tag:yaml.org,2002:str', data.data)

        def complex_representer(self, data):
            return self.represent_scalar('tag:yaml.org,2002:str', str(data))

        def uuid_representer(self, data):
            return self.represent_scalar('tag:yaml.org,2002:str', str(data))

        def enum_representer(self, data):
            return self.represent_data(data.value)

        def unknown_representer(self, data):
            if isinstance(data, tuple) and hasattr(data, '_fields'):
                return self.dict_representer(data._asdict())
            if isinstance(data, UserDict):
                return self.dict_representer(data)
            if isinstance(data, UserList):
                return self.list_representer(data)
            return self.represent_undefined(data)

    representers = (
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
        (uuid.UUID, BasicYamlDumper.uuid_representer),
        (None, BasicYamlDumper.unknown_representer),
    )

    for type_, representer in representers:
        BasicYamlDumper.add_representer(type_, representer)

    BasicYamlDumper.add_multi_representer(
        enum.Enum,
        BasicYamlDumper.enum_representer,
    )

    return BasicYamlDumper


def to_yaml(value, pretty=False, pkg=None):
    """
    Serializes the given value to YAML.

    :param value: the value to serialize
    :param pretty:
        whether or not to format the output in a more human-readable way; if
        not specified, defaults to ``False``
    :type pretty: bool
    :param pkg:
        the YAML package to use for serialization; if not specified, uses the
        first supported package found in the environment
    :type pkg: str
    :rtype: str
    """

    yaml = get_implementation(
        'YAML',
        SUPPORTED_PACKAGES,
        pkg,
    )

    options = {
        'Dumper': _build_dumper(yaml),
        'allow_unicode': True,
    }
    options['default_flow_style'] = not pretty

    return yaml.dump(value, **options).rstrip()


@lru_cache()
def _build_loaders(yaml):
    class StringedDatesYamlLoader(yaml.SafeLoader):
        # pylint: disable=no-self-use

        def timestamp_constructor(self, node):
            return node.value

    StringedDatesYamlLoader.add_constructor(
        'tag:yaml.org,2002:timestamp',
        StringedDatesYamlLoader.timestamp_constructor,
    )

    class NativeDatesYamlLoader(yaml.SafeLoader):
        # pylint: disable=no-self-use

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

    return StringedDatesYamlLoader, NativeDatesYamlLoader


def from_yaml(value, native_datetimes=True, pkg=None):
    """
    Deserializes the given value from YAML.

    :param value: the value to deserialize
    :type value: str
    :param native_datetimes:
        whether or not strings that look like dates/times should be
        automatically cast to the native objects, or left as strings; if not
        specified, defaults to ``True``
    :type native_datetimes: bool
    :param pkg:
        the YAML package to use for deserialization; if not specified, uses the
        first supported package found in the environment
    :type pkg: str
    """

    yaml = get_implementation(
        'YAML',
        SUPPORTED_PACKAGES,
        pkg,
    )

    stringed, native = _build_loaders(yaml)
    if native_datetimes:
        loader = native
    else:
        loader = stringed

    return yaml.load(value, Loader=loader)

