from django.conf import settings
from django.views.generic import FormView

from .forms import DeclarationForm

DECLARATION_SUCCESS_URL = getattr(settings, 'DECLARATION_SUCCESS_URL', '/')


DECLARATION_COOKIE_KWARGS = {
    'key': 'declaration',
    'value': '',
    'max_age': 1 * 24 * 60 * 60,
    'expires': None,
    'path': '/',
    'domain': None,
    'secure': None,
    'httponly': False,
}


class Declaration(FormView):
    """ Set the HCP declaration cookie on post. """
    cookie_kwargs = DECLARATION_COOKIE_KWARGS
    form_class = DeclarationForm
    success_url = DECLARATION_SUCCESS_URL
    template_name = 'declaration/declaration_form.html'
    template_name_ajax = 'declaration/declaration_form_ajax.html'

    def form_valid(self, form):
        next = form.cleaned_data.get('next')
        if next:
            self.success_url = next
        response = super(Declaration, self).form_valid(form)
        response.set_cookie(**self.cookie_kwargs)
        return response

    def get_template_names(self):
        if self.request.is_ajax():
            self.template_name = self.template_name_ajax
        return super(Declaration, self).get_template_names()

    def get_initial(self):
        initial = super(Declaration, self).get_initial()
        initial['next'] = self.request.GET.get('next', '')
        return initial
