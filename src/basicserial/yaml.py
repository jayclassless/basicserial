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
from io import StringIO

from .util import get_date_or_string, Implementation, ImplementationRegistry


class YamlImplementation(Implementation):  # noqa: abstract-method
    pass


class PyYamlImplementation(YamlImplementation):
    module_name = 'yaml'

    def __init__(self):
        super().__init__()

        if self.is_available():
            self._dumper = self._build_dumper()
            self._strdate_loader = self._build_strdate_loader()
            self._nativedate_loader = self._build_nativedate_loader()

    def serialize(self, value, pretty=False):
        opts = {
            'Dumper': self._dumper,
            'allow_unicode': True,
            'default_flow_style': not pretty,
        }
        return self._module.dump(value, **opts).rstrip()

    def deserialize(self, value, native_datetimes=True):
        if native_datetimes:
            loader = self._nativedate_loader
        else:
            loader = self._strdate_loader

        return self._module.load(value, Loader=loader)

    def _build_dumper(self, base_dumper=None):  # noqa: complex
        yaml = self._module
        base_dumper = base_dumper or yaml.SafeDumper

        class BasicYamlDumper(base_dumper):  # noqa: too-many-ancestors
            def list_representer(self, data):
                return self.represent_sequence(
                    'tag:yaml.org,2002:seq',
                    list(data),
                )

            def dict_representer(self, data):
                return self.represent_mapping(
                    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                    list(data.items()),
                )

            def decimal_representer(self, data):
                return self.represent_scalar(
                    'tag:yaml.org,2002:float',
                    str(data),
                )

            def time_representer(self, data):
                return self.represent_scalar(
                    'tag:yaml.org,2002:str',
                    data.isoformat(),
                )

            def userstring_representer(self, data):
                return self.represent_scalar(
                    'tag:yaml.org,2002:str',
                    data.data,
                )

            def complex_representer(self, data):
                return self.represent_scalar(
                    'tag:yaml.org,2002:str',
                    str(data),
                )

            def uuid_representer(self, data):
                return self.represent_scalar(
                    'tag:yaml.org,2002:str',
                    str(data),
                )

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

    def _build_strdate_loader(self, base_loader=None):
        yaml = self._module
        base_loader = base_loader or yaml.SafeLoader

        class StringedDatesYamlLoader(base_loader):
            # pylint: disable=no-self-use

            def timestamp_constructor(self, node):
                return node.value

        StringedDatesYamlLoader.add_constructor(
            'tag:yaml.org,2002:timestamp',
            StringedDatesYamlLoader.timestamp_constructor,
        )

        return StringedDatesYamlLoader

    def _build_nativedate_loader(self, base_loader=None):
        yaml = self._module
        base_loader = base_loader or yaml.SafeLoader

        class NativeDatesYamlLoader(base_loader):
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

        return NativeDatesYamlLoader


class RuamelYamlImplementation(PyYamlImplementation):
    module_name = 'ruamel.yaml'

    def __init__(self):
        super().__init__()

        self._new_api = self._module and (self._module.version_info >= (0, 15))

    def _build_dumper(self, base_dumper=None):  # noqa: complex
        return super()._build_dumper(
            base_dumper=self._module.representer.SafeRepresenter,
        )

    def _build_strdate_loader(self, base_loader=None):
        return super()._build_strdate_loader(
            base_loader=self._module.constructor.SafeConstructor,
        )

    def _build_nativedate_loader(self, base_loader=None):
        return super()._build_nativedate_loader(
            base_loader=self._module.constructor.SafeConstructor,
        )

    def serialize(self, value, pretty=False):
        if self._new_api:
            yaml = self._module.YAML(typ='safe')
            yaml.allow_unicode = True
            yaml.default_flow_style = not pretty
            yaml.Representer = self._dumper
            buf = StringIO()
            yaml.dump(value, buf)
            return buf.getvalue().rstrip()

        opts = {
            'Dumper': self._dumper,
            'allow_unicode': True,
            'default_flow_style': not pretty,
        }
        return self._module.dump(value, **opts).rstrip()

    def deserialize(self, value, native_datetimes=True):
        if native_datetimes:
            loader = self._nativedate_loader
        else:
            loader = self._strdate_loader

        if self._new_api:
            yaml = self._module.YAML(typ='safe')
            yaml.Constructor = loader
            return yaml.load(value)

        return self._module.load(value, Loader=loader)


IMPLEMENTATIONS = ImplementationRegistry()
IMPLEMENTATIONS.register('yaml', PyYamlImplementation)
IMPLEMENTATIONS.register('ruamel.yaml', RuamelYamlImplementation)


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

    impl = IMPLEMENTATIONS.get(pkg)
    return impl.serialize(value, pretty=pretty)


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

    impl = IMPLEMENTATIONS.get(pkg)
    return impl.deserialize(value, native_datetimes=native_datetimes)
