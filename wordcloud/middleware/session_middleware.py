from django.middleware import csrf
from django.contrib.sessions import middleware


class SessionMiddleware(middleware.SessionMiddleware):
    def __init__(self, get_response=None):
        super(SessionMiddleware, self).__init__(get_response)
        bases = (SessionHeaderMixin, self.SessionStore)
        self.SessionStore = type('SessionStore', bases, {})

    def process_request(self, request):
        super(SessionMiddleware, self).process_request(request)
        sessionid = request.META.get(u'HTTP_X_SESSIONID')
        if not sessionid:
            print('No sessionid in headers. Try the POST params ...')
            sessionid = request.POST.get('session_key')
        if sessionid:
            request.session = self.SessionStore(sessionid)
            request.session.csrf_exempt = True

    def process_response(self, request, response):
        supr = super(SessionMiddleware, self)
        response = supr.process_response(request, response)
        if request.session.session_key:
            response['X-SessionID'] = request.session.session_key
        return response


class CsrfViewMiddleware(csrf.CsrfViewMiddleware):
    def process_view(self, request, *args, **kwargs):
        if not request.session.csrf_exempt:
            supr = super(CsrfViewMiddleware, self)
            return supr.process_view(request, *args, **kwargs)


class SessionHeaderMixin(object):
    def __init__(self, session_key=None):
        super(SessionHeaderMixin, self).__init__(session_key)
        self.csrf_exempt = False
