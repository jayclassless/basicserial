from collections import namedtuple, OrderedDict, defaultdict, UserDict, UserList, UserString
from enum import Enum
from datetime import date, time, datetime
from decimal import Decimal
from fractions import Fraction
from pytz import timezone

import pytest


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


def pkg_parameterize(packages, vectors):
    return (
        (pkg, test, expected)
        for pkg in packages
        for test, expected in vectors
    )

