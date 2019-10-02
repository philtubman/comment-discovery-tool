__author__ = 'vaibhav'

try:
    import cProfile as profile
except ImportError:
    import profile
import pstats
from cStringIO import StringIO
from django.conf import settings
from django.template.loader import render_to_string


class ProfileMiddleware(object):

    def can(selfself, request):
        return settings.DEBUG and 'prof' in request.GET

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if self.can(request):
            self.profiler = profile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):

        if self.can(request):
            self.profiler.create_stats()
            io = StringIO()
            stats = pstats.Stats(self.profiler, stream=io)
            stats.strip_dirs().sort_stats(request.GET.get('sort', 'time'))
            stats.print_stats(int(request.GET.get('count', 100000)))

            stats_str = io.getvalue()
            profile_output = stats_str.split('\n')
            info = '\n'.join(profile_output[:4])
            table_header = [_ for _ in profile_output[4].split(' ') if _]
            table_rows = [[int(_.split()[0].split('/')[0])] + _.split()[1:] for _ in profile_output[5:-3] if _]
            table_rows = [_[:5] + [' '.join(_[5:])] for _ in table_rows]

            ret_dict = dict(table_header=table_header,
                            table_rows=table_rows,
                            info=info)

            response.content = render_to_string('profiler/profiler.html', ret_dict)
        return response