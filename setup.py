#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import dirname, join
import os
import sys

# When creating the sdist, make sure the django.mo file also exists:
try:
    os.chdir('any_urlfield')
    try:
        from django.core.management.commands.compilemessages import compile_messages
        compile_messages(sys.stderr)
    except ImportError:
        pass
finally:
    os.chdir('..')


setup(
    name='django-any-urlfield',
    version='1.0.1',
    license='Apache License, Version 2.0',

    description='An improved URL selector to choose between internal models and external URLs',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-any-urlfield',
    download_url='https://github.com/edoburu/django-any-urlfield/zipball/master',

    packages=find_packages(exclude=('example*',)),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)
