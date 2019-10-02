import re

from unittest.mock import Mock, patch

from django.test import TestCase

from ..middleware import DeclarationMiddleware
from ..views import DECLARATION_COOKIE_KWARGS


class DeclarationMiddlewareTest(TestCase):
    def setUp(self):
        self.dm = DeclarationMiddleware()
        self.request = Mock()
        self.request.path_info = '/'
        self.request.COOKIES = {}

    def set_cookie(self):
        cookie = DECLARATION_COOKIE_KWARGS['value']
        self.request.COOKIES[DECLARATION_COOKIE_KWARGS['key']] = cookie

    def test_has_cookie_false(self):
        self.assertFalse(self.dm.has_cookie(self.request))

    def test_has_cookie_true(self):
        self.set_cookie()
        self.assertTrue(self.dm.has_cookie(self.request))

    def test_has_cookie_missing(self):
        del self.request.COOKIES
        self.assertFalse(self.dm.has_cookie(self.request))

    def test_is_protected_declaration_url(self):
        self.request.path_info = self.dm.declaration_url
        self.assertFalse(self.dm.is_protected(self.request))

    def test_is_protected_match(self):
        self.request.path_info = '/same-url/'
        self.dm.protected = re.compile(r'^' + self.request.path_info)
        self.assertTrue(self.dm.is_protected(self.request))

    def test_is_protected_no_match(self):
        self.dm.protected = re.compile(r'^/some-url/')
        self.request.path_info = '/someo-other-url/'
        self.assertFalse(self.dm.is_protected(self.request))

    def test_redirect(self):
        response = self.dm.redirect(self.request)
        expected = '{0}?next={1}'.format(
            self.dm.declaration_url,
            self.request.path_info
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], expected)

    @patch('declaration.middleware.DeclarationMiddleware.has_cookie')
    def test_process_request_cookie_true(self, has_cookie):
        has_cookie.return_value = True
        self.assertEqual(self.dm.process_request(self.request), None)
        has_cookie.assert_called_once_with(self.request)

    @patch('declaration.middleware.DeclarationMiddleware.redirect')
    @patch('declaration.middleware.DeclarationMiddleware.is_protected')
    @patch('declaration.middleware.DeclarationMiddleware.has_cookie')
    def test_process_request_not_protected(self, has_cookie, is_protected, redirect):
        has_cookie.return_value = False
        is_protected.return_value = False

        self.assertEqual(self.dm.process_request(self.request), None)
        has_cookie.assert_called_once_with(self.request)
        is_protected.assert_called_once_with(self.request)
        self.assertFalse(redirect.called)

    @patch('declaration.middleware.DeclarationMiddleware.redirect')
    @patch('declaration.middleware.DeclarationMiddleware.is_protected')
    @patch('declaration.middleware.DeclarationMiddleware.has_cookie')
    def test_process_request(self, has_cookie, is_protected, redirect):
        has_cookie.return_value = False
        is_protected.return_value = True

        self.assertEqual(self.dm.process_request(self.request), redirect.return_value)
        has_cookie.assert_called_once_with(self.request)
        is_protected.assert_called_once_with(self.request)
        redirect.assert_called_once_with(self.request)
