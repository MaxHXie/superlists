from django.urls import resolve
from django.test import TestCase
from django.http import HttpRequest

from lists.views import home_page

class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        # resolve is the function Django uses internally to resolve URLs and find what view
        # function they should map to. We're checking that resolve, when called with "/",
        # the root of the site, finds a function called home_page
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        # We create an HttpRequest object, which is what Django will see when a user's
        # browser asks for a page
        request = HttpRequest()
        # We pass it to our home_page view, which gives us a response. You won't be sur-
        # prised to hear that this object is an instance of a class called HttpResponse
        response = home_page(request)
        # Then, we extract the .content of the response. These are the raw bytes, the ones
        # and zeros that would be sent down the wire to the user's browser. We call
        # .decode() to convert them into the string of HTML that's being sent to the user.
        html = response.content.decode('utf8')
        # We want it to start with an <html> tag which gets closed at the end.
        self.assertTrue(html.startswith('<html>'))
        # And we want a <title> tag somewhere in the middle, with the words "To-Do lists" in it
        # because that's what we specified in our functional test.
        self.assertIn('<title>To-Do lists</title>', html)
        self.assertTrue(html.endswith('</html>'))
