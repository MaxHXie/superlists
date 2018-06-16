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

    def test_can_save_a_POST_request(self):
        response = self.client.post('/', data={'item_text': 'A new list item'})
        self.assertIn('A new list item', response.content.decode())
        self.assertTemplateUsed(response, 'home.html')

'''
Red/Green/Refactor and Triangulation

The unit-test/code cycle is sometimes taught as Red, Green, Refactor

    - Start by writing a unit test which fails (Red).
    - Write the simplest possible code to get it to pass (Green), even if that means cheating.
    - Refactor to get to better code that makes more sense.

So what do we do during the Refactoring stage? What justifies moving from an implementation
where we "cheat" to one we're happy with?

One methodology is eliminate duplication: if your test uses a magic constant (like the
"1:" in front of our list item), and your application code also uses it, that counts as a
duplication, so it justifies refactoring. Removing the magic constant from the application code
usually means you have to stop cheating.

I find that leaves things a little too vague, so I usually like to use a second technique, which is
called triangulation: if your tests let you get away with writing "cheating" code that you're
not happy with, like returning a magic constant, write another test that forces you to write
some better code. That's what we're doing when we extend the FT to check that we get "2:"
when inputting a second list item.

'''
