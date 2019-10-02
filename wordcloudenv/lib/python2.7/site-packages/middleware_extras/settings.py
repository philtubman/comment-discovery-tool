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


from django.conf import settings

#REVERSE_PROXY_HTTPS_HEADERS = [
#    ('x-forwarded-protocol', 'https'),
#    ('x-forwarded-ssl', 'on'),
#]
# This should be a list containing tuples of the format:
#   (header_name, header_value)
# These headers could be anything and it is encouraged that header names that
# are hard to guess should be used.
# See ticket for more info:
#   http://code.djangoproject.com/ticket/14597#comment:3
REVERSE_PROXY_HTTPS_HEADERS = getattr(settings, 'REVERSE_PROXY_HTTPS_HEADERS', ())

# List of URLs that should be redirected to the HTTPS version of the resource 
SSL_REQUIRE_URLS = getattr(settings, 'SSL_REQUIRED_URLS', [])

# If set to True and a URL that matches a URL of the SSL_REQUIRE_URLS list,
# then, in case the URL is accessed over HTTP, it is redirected to the HTTPS
# version. If it set to False, the client in the same occasion is forbidden
# access.
SSL_REQUIRE_REDIRECT = getattr(settings, 'SSL_REQUIRE_REDIRECT', True)

