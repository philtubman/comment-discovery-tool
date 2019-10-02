from django.test import RequestFactory, TestCase

from ..forms import DeclarationForm
from ..views import Declaration, DECLARATION_COOKIE_KWARGS, DECLARATION_SUCCESS_URL


class TestDeclarationViews(TestCase):
    cookie_data = DECLARATION_COOKIE_KWARGS

    def test_get(self):
        view = Declaration.as_view()
        request = RequestFactory().get('/')
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data['form'], DeclarationForm)

        # Check the cookie is not set
        self.assertNotIn(self.cookie_data['key'], response.cookies)

    def test_ajax_template_names(self):
        view = Declaration()
        view.request = RequestFactory().get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        template_names = view.get_template_names()

        self.assertEqual(template_names, ['declaration/declaration_form_ajax.html'])

    def test_template_names(self):
        view = Declaration()
        view.request = RequestFactory().get('/')
        template_names = view.get_template_names()

        self.assertEqual(template_names, ['declaration/declaration_form.html'])

    def test_post(self):
        view = Declaration.as_view()
        request = RequestFactory().post('/')
        response = view(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], DECLARATION_SUCCESS_URL)

        # Check the cookie is set
        self.assertIn(self.cookie_data['key'], response.cookies)
        cookie = response.cookies[self.cookie_data['key']]
        self.assertEqual(cookie.value, self.cookie_data['value'])
        self.assertEqual(cookie.get('path'), self.cookie_data['path'])
        self.assertEqual(cookie.get('max-age'), 1 * 24 * 60 * 60)

    def test_post_next(self):
        view = Declaration.as_view()
        data = {'next': '/next/'}
        request = RequestFactory().post('/', data)
        response = view(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], data['next'])
