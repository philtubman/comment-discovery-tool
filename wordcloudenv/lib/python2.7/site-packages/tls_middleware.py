from threading import local

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError as ie:
    MiddlewareMixin = object

_tls = local()


def get_user():
    """
    :return: User
   """
    return getattr(_tls, 'user', None)


def get_request():
    """
    :return: <WSGIRequest:>
    """
    return getattr(_tls, 'request', None)


class TLSMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # set request and user to tls
        _tls.request = request
        _tls.user = getattr(request, 'user', None)

    def process_response(self, request, response):
        # clean request and user after response
        _tls.request = None
        _tls.user = None
        return response

    def process_exception(self, request, exception):
        # clean request and user after exception
        _tls.request = None
        _tls.user = None
