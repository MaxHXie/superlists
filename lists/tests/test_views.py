import unittest
from unittest.mock import patch, Mock
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from django.utils.html import escape
from unittest import skip
import time
from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR,
    ExistingListItemForm, ItemForm,
)
from lists.models import Item, List
from lists.views import new_list, new_list
User = get_user_model()


class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class NewListViewIntegratedTest(TestCase):

    def test_can_save_a_POST_request(self):
        # Sending a post request with a non-empty text variable creates a list with that text
        self.client.post('/lists/new', data={'text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_for_invalid_input_doesnt_save_but_shows_errors(self):
        # Sending a post request with an empty text-variable will not create a list
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        # If user is authenticated, the owner of that list will be that user
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text': 'new item'})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)

    @patch('lists.views.List')
    @patch('lists.views.ItemForm')
    def test_list_owner_if_saved_if_user_is_authenticated(
        self, mockItemFormClass, mockListClass
    ):
        # The owner of the list is saved if the user is authenticated
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        mock_list = mockListClass.return_value

        def check_owner_assigned():
            self.assertEqual(mock_list.owner, user)
        mock_list.save.side_effect = check_owner_assigned

        self.client.post('/lists/new', data={'text': 'new item'})

        mock_list.save_assert_called_once_with()


@skip
@patch('lists.views.NewListForm')
class NewListViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'

    def test_passes_POST_data_to_NewListForm(self, mockNewListForm):
        # The new_list view sends POST data to NewListForm
        new_list(self.request)
        mockNewListForm.assert_called_once_with(data=self.request.POST)


    def test_saves_form_with_owner_if_form_valid(self, mockNewListForm):
        # If the form is valid, the owner is saved as a parameter in the NewListForm "save" method
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)


    def test_does_not_save_if_form_invalid(self, mockNewListForm):
        # The form does not save if it is invalid
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        new_list(self.request)
        self.assertFalse(mock_form.save.called)

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(
        self, mock_redirect, mockNewListForm
    ):
        # If the form is valid, the user is redirected with "redirect(list_)"
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True

        response = new_list(self.request)

        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value)


    @patch('lists.views.render')
    def test_renders_home_template_with_form_if_form_invalid(
        self, mock_render, mockNewListForm
    ):
        # If the form is invalid, the home template is rendered
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False

        response = new_list(self.request)

        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
            self.request, 'home.html', {'form': mock_form}
        )

@skip
class ListViewTest(TestCase):

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')


    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')


    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)


    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )
        self.assertRedirects(response, f'/lists/{correct_list.id}/')


    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))


    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')
        response = self.client.post(
            f'/lists/{list1.id}/',
            data={'text': 'textey'}
        )

        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.all().count(), 1)


@skip
class MyListsTest(TestCase):

    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com')
        self.assertTemplatesUsed(response, 'my_lists.html')

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email='wrong@owner.com')
        correct_user = User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)

class ShareListTest(TestCase):
    def test_post_redirects_to_list_lists_page(self):
        user = User.objects.create(email="a@b.com")
        list_ = List.objects.create()
        response = self.client.post(f'/lists/{list_.id}/share', {'sharee': user.email})
        self.assertRedirects(response, list_.get_absolute_url())

    def test_sharing_a_list_via_post(self):
        user = User.objects.create(email='a@b.com')
        list_ = List.objects.create()
        self.client.post(f'/lists/{list_.id}/share', {'sharee': user.email})
        self.assertIn(user, list_.shared_with.all())
























"""
    def test_sharing_a_list_via_post(self):
        sharee = User.objects.create(email='share.with@me.com')
        list_ = List.objects.create()
        self.client.post(
            f'/lists/{list_.id}/share',
            {'sharee': 'share.with@me.com'}
        )
        self.assertIn(sharee, list_.shared_with.all())


    def test_redirects_after_POST(self):
        sharee = User.objects.create(email='share.with@me.com')
        list_ = List.objects.create()
        response = self.client.post(
            f'/lists/{list_.id}/share',
            {'sharee': 'share.with@me.com'}
        )
        self.assertRedirects(response, list_.get_absolute_url())
"""
