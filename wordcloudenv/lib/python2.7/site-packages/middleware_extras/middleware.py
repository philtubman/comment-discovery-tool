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

"""
CHECK THESE:

http://djangosnippets.org/snippets/1706/
http://djangosnippets.org/snippets/1999/
http://djangosnippets.org/snippets/85/
http://djangosnippets.org/snippets/240/
"""

from middleware_extras import settings
from middleware_extras.utils import get_formatted_headers


class ReverseProxyHttpsHeadersMiddleware(object):
    
    def process_request(self, request):
        """
        
        Based on ticket by gnotaras: http://code.djangoproject.com/ticket/14597
        
        All headers must match
        All header values must match
        """
        if not settings.REVERSE_PROXY_HTTPS_HEADERS:
            return
        https_headers = get_formatted_headers(settings.REVERSE_PROXY_HTTPS_HEADERS)
        for header_name, header_value in https_headers:
            if header_name not in request.META:
                return
            elif request.META[header_name].lower() != header_value:
                return
        request.META['HTTPS'] = 'on'




class CompactHTMLMiddleware(object):
    """Middleware that strips white space between HTML tags from the
    response content.
    
    Add it last to the list of MIDDLEWARE_CLASSES:
    
    MIDDLEWARE_CLASSES = (
        ...
        'middleware_extras.middleware.CompactHTMLMiddleware'
    )
    """
    
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            
            #from django.utils.html import strip_spaces_between_tags
            #response.content = strip_spaces_between_tags(response.content)
            
            from slimmer import xhtml_slimmer
            response.content = xhtml_slimmer(response.content)
            
        return response


class PrettifyHTMLMiddleware(object):
    """Middleware that prettifies HTML.
    
    Add it last to the list of MIDDLEWARE_CLASSES:
    
    MIDDLEWARE_CLASSES = (
        ...
        'middleware_extras.middleware.PrettifyHTMLMiddleware'
    )
    """
    
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            
            # Beautify HTML for development
            from BeautifulSoup import BeautifulSoup
            soup = BeautifulSoup(response.content)
            response.content = soup.prettify()
        
        return response

