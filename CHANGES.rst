**********************
basicserial Change Log
**********************

.. contents:: Releases


1.1.0 (2020-03-15)
==================

* Added support for handling ``enum.Enum`` members.
* Added support for handling ``uuid.UUID`` objects.
* Added the ability to explicitly specify the serialization package to use via
  a ``pkg`` argument.
* Added support for using the ``simplejson``, ``orjson``, ``rapidjson``,
  ``ujson``, ``hyperjson``, ``qtoml``, and ``tomlkit`` libraries.


1.0.0 (2020-01-10)
==================

* Removed Python 2 support.


0.2.0 (2019-04-27)
==================

* Fixed an issue with pretty-printing YAML that arose with the new version of
  PyYAML.


0.1.0 (2018-06-09)
==================

* Initial public release.

