import logging
from django.http import HttpResponseRedirect
from django.core.urlresolvers import resolve, reverse, NoReverseMatch

logger = logging.getLogger("middleware_public_pages")

class PublicPagesMiddleware(object):
    """
    This middleware will check if there is a version of this page for not-authenticated users. (the same URL-name with
    the suffix '_pub') and will redirect the request
    """

    def process_request(self, request):
        if not request.user.is_authenticated:
            url_resolver = resolve(request.path)
            url_name = url_resolver.url_name

            if url_name and not url_name.endswith("_pub"):
                url_name += "_pub"
                try:
                    rev_url = reverse(viewname=url_name, args=url_resolver.args, kwargs=url_resolver.kwargs)
                    if rev_url == request.path:
                        logger.error("Recursive error: Both pages [name] and [name]_pub are generating the same "
                                     "url. Aborting the redirect to avoid recursive requests.")
                    else:
                        return HttpResponseRedirect(rev_url, )
                except NoReverseMatch:
                    # There is no 'public' version of this url, continue the process normaly..
                    pass
