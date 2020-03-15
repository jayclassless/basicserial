from collections import namedtuple, OrderedDict, defaultdict, UserDict, UserList, UserString
from enum import Enum
from datetime import date, time, datetime
from decimal import Decimal
from fractions import Fraction
from pytz import timezone
from uuid import uuid4

import pytest

from basicserial.util import get_implementation


class CustomUserDict(UserDict):
    pass


class CustomUserList(UserList):
    pass


class CustomUserString(UserString):
    pass


class CustomEnum(Enum):
    an_int = 1
    a_str = 'foo'
    a_bool = False


CustomNamedTuple = namedtuple('CustomNamedTuple', ['foo'])


TZ_EST = timezone('America/New_York')
TZ_UTC = timezone('UTC')


SOME_UUID = uuid4()


def pkg_parameterize(packages, vectors):
    return (
        (pkg, test, expected)
        for pkg in packages
        for test, expected in vectors
    )


def strip_missing_pkg(supported):
    stripped = []
    for pkg in supported:
        try:
            get_implementation(hash(supported), supported, pkg)
        except ValueError:
            pass
        else:
            stripped.append(pkg)
    return stripped

