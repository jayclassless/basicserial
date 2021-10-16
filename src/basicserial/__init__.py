#
# Copyright (c) 2018, Jason Simeone
#

from .json import (
    to_json,
    from_json,
    IMPLEMENTATIONS as JSON_IMPLEMENTATIONS,
)

from .toml import (
    to_toml,
    from_toml,
    IMPLEMENTATIONS as TOML_IMPLEMENTATIONS,
)

from .yaml import (
    to_yaml,
    from_yaml,
    IMPLEMENTATIONS as YAML_IMPLEMENTATIONS,
)

SUPPORTED_JSON_PACKAGES = JSON_IMPLEMENTATIONS.registered_packages
AVAILABLE_JSON_PACKAGES = JSON_IMPLEMENTATIONS.available_packages
SUPPORTED_YAML_PACKAGES = YAML_IMPLEMENTATIONS.registered_packages
AVAILABLE_YAML_PACKAGES = YAML_IMPLEMENTATIONS.available_packages
SUPPORTED_TOML_PACKAGES = TOML_IMPLEMENTATIONS.registered_packages
AVAILABLE_TOML_PACKAGES = TOML_IMPLEMENTATIONS.available_packages

__all__ = (
    'to_json',
    'from_json',
    'SUPPORTED_JSON_PACKAGES',
    'AVAILABLE_JSON_PACKAGES',

    'to_yaml',
    'from_yaml',
    'SUPPORTED_YAML_PACKAGES',
    'AVAILABLE_YAML_PACKAGES',

    'to_toml',
    'from_toml',
    'SUPPORTED_TOML_PACKAGES',
    'AVAILABLE_TOML_PACKAGES',
)
