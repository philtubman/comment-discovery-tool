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

from middleware_extras import settings


def get_formatted_headers():
    """
    This function returns a list that contains the same (header_name, value)
    tuples as the REVERSE_PROXY_HTTPS_HEADERS setting. Several transformations
    have been applied to the headers so as to be in the format which is used
    in the Django request object.
    
    For instance:
    
        X-Forwarded-Ssl  -->  HTTP_X_FORWARDED_SSL
    
    """
    headers = []
    for header_name, header_value in settings.REVERSE_PROXY_HTTPS_HEADERS:
        header_name = header_name.replace('-', '_')
        headers.append(('HTTP_%s' % header_name.strip().upper()), header_value.lower())
    return headers

