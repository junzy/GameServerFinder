#! /usr/bin/env python
# coding=utf-8

import setuptools
import io

import pygamescanner


def read(*file_names, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in file_names:
        with io.open(filename, encoding=encoding) as file_obj:
            buf.append(file_obj.read())
    return sep.join(buf)


LONG_DESCRIPTION = read('README.rst', 'CHANGELOG.rst')

setuptools.setup(
    name=pygamescanner.__package_name__,
    version=pygamescanner.__version__,
    url=pygamescanner.__url__,
    license=pygamescanner.__license__,
    author=pygamescanner.__author__,
    tests_require=[],
    install_requires=[
        'twisted>=12.0.0',
        'netaddr>=0.7.10',
        'lockfile>=0.9.1',
        'python-daemon>=1.5.5'
    ],
    cmdclass={},
    author_email=pygamescanner.__email__,
    description=pygamescanner.__description__,
    long_description=LONG_DESCRIPTION,
    packages=[pygamescanner.__package_name__],
    include_package_data=True,
    platforms='any',
    test_suite='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: No Input/Output (Daemon)',
        'Framework :: Twisted',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'Topic :: Games/Entertainment',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: Utilities'
    ],
    extras_require={}
)
