***********
basicserial
***********

.. image:: https://img.shields.io/pypi/v/basicserial.svg
   :target: https://pypi.python.org/pypi/basicserial
.. image:: https://img.shields.io/pypi/l/basicserial.svg
   :target: https://pypi.python.org/pypi/basicserial
.. image:: https://github.com/jayclassless/basicserial/workflows/Test/badge.svg
   :target: https://github.com/jayclassless/basicserial/actions

.. contents:: Contents


Overview
--------
Does this look familiar?

::

    >>> import json
    >>> from datetime import date
    >>> MY_DATA = {'foo': 123, 'bar': date(2018, 5, 22)}
    >>> json.dumps(MY_DATA)
    Traceback (most recent call last):
        ...
    TypeError: datetime.date(2018, 5, 22) is not JSON serializable

It's one thing when your serialization tools don't know how to handle your
custom classes, but it's annoying when they don't handle the built-in and/or
common data types. Thus, ``basicserial`` was born.

This package is a thin wrapper around the common serialization tools that can
do the following for you when working with JSON, YAML, and TOML:

* Automatically serializes the following types to common-sense representations:

  .. list-table::
     :header-rows: 1

     * - Type
       - JSON
       - YAML
       - TOML
     * - `set <https://docs.python.org/2/library/stdtypes.html#set>`_
       - array
       - sequence
       - array
     * - `frozenset <https://docs.python.org/2/library/stdtypes.html#frozenset>`_
       - array
       - sequence
       - array
     * - `Decimal <https://docs.python.org/2/library/decimal.html>`_
       - number
       - float
       - float
     * - `Fraction <https://docs.python.org/2/library/fractions.html>`_
       - string
       - string
       - string
     * - `date <https://docs.python.org/2/library/datetime.html#date-objects>`_
       - string (ISO 8601)
       - timestamp
       - string (ISO 8601)
     * - `time <https://docs.python.org/2/library/datetime.html#time-objects>`_
       - string (ISO 8601)
       - string (ISO 8601)
       - string (ISO 8601)
     * - `datetime <https://docs.python.org/2/library/datetime.html#datetime-objects>`_
       - string (ISO 8601)
       - timestamp
       - string (ISO 8601)
     * - `complex <https://docs.python.org/2/library/functions.html#complex>`_
       - string
       - string
       - string
     * - `OrderedDict <https://docs.python.org/2/library/collections.html#collections.OrderedDict>`_
       - object
       - map
       - key/value
     * - `defaultdict <https://docs.python.org/2/library/collections.html#defaultdict-objects>`_
       - object
       - map
       - key/value
     * - `namedtuple <https://docs.python.org/2/library/collections.html#namedtuple-factory-function-for-tuples-with-named-fields>`_
       - object
       - map
       - key/value
     * - `UserDict <https://docs.python.org/2/library/userdict.html>`_
       - object
       - map
       - key/value
     * - `UserList <https://docs.python.org/2/library/userdict.html#module-UserList>`_
       - array
       - sequence
       - array
     * - `UserString <https://docs.python.org/2/library/userdict.html#module-UserString>`_
       - string
       - string
       - string

* Can automatically deserialize dates, times, and datetimes into the native
  Python objects.

* Provides a simple flag for generating "pretty" strings.


Usage
=====
To use this package, install it from PyPI (``pip install basicserial``). Then,
if you want to use YAML or TOML, you'll also need to install a package that
provides that functionality (for YAML ``basicserial`` supports `PyYAML
<https://pypi.org/project/PyYAML>`_ and `ruamel.yaml
<https://pypi.org/project/ruamel.yaml>`_, for TOML it supports `toml
<https://pypi.org/project/toml>`_ or `pytoml
<https://pypi.org/project/pytoml>`_). ``basicserial`` will use Python's
built-in `json <https://docs.python.org/2/library/json.html>`_ module to handle
JSON.

JSON::

    >>> print(basicserial.to_json(MY_DATA))
    {"foo": 123, "bar": "2018-05-22"}

    >>> print(basicserial.to_json(MY_DATA, pretty=True))
    {
      "foo": 123,
      "bar": "2018-05-22"
    }

    >>> basicserial.from_json(basicserial.to_json(MY_DATA))
    {u'foo': 123, u'bar': datetime.date(2018, 5, 22)}

    >>> basicserial.from_json(basicserial.to_json(MY_DATA), native_datetimes=False)
    {u'foo': 123, u'bar': u'2018-05-22'}


YAML::

    >>> print(basicserial.to_yaml(MY_DATA))
    {bar: 2018-05-22, foo: 123}

    >>> print(basicserial.to_yaml(MY_DATA, pretty=True))
    bar: 2018-05-22
    foo: 123

    >>> basicserial.from_yaml(basicserial.to_yaml(MY_DATA))
    {u'foo': 123, u'bar': datetime.date(2018, 5, 22)}

    >>> basicserial.from_yaml(basicserial.to_yaml(MY_DATA), native_datetimes=False)
    {'foo': 123, 'bar': u'2018-05-22'}


TOML::

    >>> print(basicserial.to_toml(MY_DATA))
    foo = 123
    bar = "2018-05-22"

    >>> print(basicserial.to_toml(MY_DATA, pretty=True))
    foo = 123
    bar = "2018-05-22"

    >>> basicserial.from_toml(basicserial.to_toml(MY_DATA))
    {u'foo': 123, u'bar': datetime.date(2018, 5, 22)}

    >>> basicserial.from_toml(basicserial.to_toml(MY_DATA), native_datetimes=False)
    {u'foo': 123, u'bar': u'2018-05-22'}


License
-------
This project is released under the terms of the `MIT License`_.

.. _MIT License: https://opensource.org/licenses/MIT

