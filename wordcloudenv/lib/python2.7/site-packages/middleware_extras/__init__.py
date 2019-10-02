# -*- coding: utf-8 -*-
#
#  This file is part of django-middleware-extras.
#
#  django-middleware-extras provides some extra middleware classes that are often needed by Django projects.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-middleware-extras
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-middleware-extras
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

VERSION = (0, 1, 2, 'final', 0)

def get_version():
    version = '%d.%d.%d' % (VERSION[0], VERSION[1], VERSION[2])
    return version


long_description = """
This is a fairly simple Django application that provides some extra middleware
classes which are often needed by many other Django applications.

More information about the installation, configuration and usage of this app
can be found in the *HELP* file inside the distribution package or in the
project's `wiki <http://www.codetrax.org/projects/django-middleware-extras/wiki>`_.

In case you run into any problems while using this application it is highly
recommended you file a report at the project's
`issue tracker <http://www.codetrax.org/projects/django-middleware-extras/issues>`_.

"""
