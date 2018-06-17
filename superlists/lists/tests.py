from django.urls import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string
from lists.models import Item

from lists.views import home_page

class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

        # When refactoring, work on either the code or the tests,
        # but not both at once.

        # Also: Keep refactoring and functionality changes entirely separate!

    #Each unit test should not be too long. If it is and you notice that it is testing more
    #than one thing. Divide it up and write multiple, separate unittests!!

    def test_saving_and_retrieving(self):
            first_item = Item()
            first_item.text = 'The first (ever) list item'
            first_item.save()

            second_item = Item()
            second_item.text = 'Item the second'
            second_item.save()

            saved_items = Item.objects.all()
            self.assertEqual(saved_items.count(), 2)

            first_saved_item = saved_items[0]
            second_saved_item = saved_items[1]
            self.assertEqual(first_saved_item.text, "The first (ever) list item")
            self.assertEqual(second_saved_item.text, "Item the second")

    def test_only_saves_when_necessary(self):
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)

class ListViewTest(TestCase):
    def test_displays_all_items(self):
        # Here is a new helper method: instead of using the slightly annoying assertIn/
        #response.content.decode() dane, DJango provides the assertContains
        #method, which knows how to deal with responses and trhe bytes of their content.
        Item.objects.create(text = 'itemey 1')
        Item.objects.create(text = 'itemey 2')

        response = self.client.get('/lists/the-only-list-in-the-world/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')

    def test_uses_list_template(self):
        response = self.client.get('/lists/the-only-list-in-the-world/')
        self.assertTemplateUsed(response, 'list.html')

class NewListTest(TestCase):

    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'item_text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        self.assertRedirects(response, '/lists/the-only-list-in-the-world/')

'''
This is another place to pay attention to trailing slashes, incidentally. It's /new, with no
trailing slash.

The convetion I am using is that URLs without a trailing slash are "action"
URLs which modify the database.
'''
