from django.urls import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string

from lists.views import home_page

class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

        # When refactoring, work on either the code or the tests,
        # but not both at once.

        # Also: Keep refactoring and functionality changes entirely separate!
