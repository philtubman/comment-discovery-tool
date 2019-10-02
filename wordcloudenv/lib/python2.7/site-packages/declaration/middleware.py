import re

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.template.defaultfilters import urlencode

from .views import DECLARATION_COOKIE_KWARGS


PROTECTED_URL_PATTERNS = settings.PROTECTED_URL_PATTERNS


class DeclarationMiddleware(object):
    """
    Redirect all requests that match a path to the declaration page unless a
    cookie has been set.  The declaration page includes a form and sets the
    cookie on post.
    """

    declaration_url = reverse_lazy('declaration:form')
    protected = re.compile(r'({})'.format('|'.join(PROTECTED_URL_PATTERNS)))
    cookie_key = DECLARATION_COOKIE_KWARGS['key']

    def process_request(self, request):
        if self.has_cookie(request):
            return

        if self.is_protected(request):
            return self.redirect(request)

    def redirect(self, request):
        # Redirect to declaration_url
        url = '{0}?next={1}'.format(
            self.declaration_url,
            urlencode(request.path_info),
        )
        return HttpResponseRedirect(url)

    def has_cookie(self, request):
        if not hasattr(request, 'COOKIES'):
            return False
        return self.cookie_key in request.COOKIES

    def is_protected(self, request):
        path = request.path_info
        return path != self.declaration_url and self.protected.match(path)
