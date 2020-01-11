#
# Copyright (c) 2018, Jason Simeone
#

from setuptools import setup, find_packages


setup(
    name='basicserial',
    version='1.0.0',
    description='A convenience wrapper around serialization libraries to'
    ' handle common tasks.',
    long_description=open('README.rst', 'r').read(),
    keywords='serialize serialization json yaml toml',
    author='Jason Simeone',
    author_email='jay@classless.net',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Development Status :: 5 - Production/Stable',
    ],
    url='https://github.com/jayclassless/basicserial',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=True,
    include_package_data=True,
    install_requires=[
        'iso8601',
    ],
)

