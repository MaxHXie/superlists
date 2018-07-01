from selenium import webdriver
from .base import FunctionalTest
from .list_page import ListPage
from .my_lists_page import MyListsPage
from django.contrib.auth import get_user_model
from .management.commands.create_session import create_pre_authenticated_session
from selenium.webdriver.common.keys import Keys
from django.core import mail
import os
import poplib
import re
from accounts.models import Token
User = get_user_model()
import time

def quit_if_possible(browser):
    try:
        browser.quit()
    except:
        pass

SUBJECT = 'Your login link for Superlists'

class SharingTest(FunctionalTest):

    def wait_for_email(self, test_email, subject, hej):
        if not self.staging_server:
            email = mail.outbox[hej]
            self.assertIn(test_email, email.to)
            self.assertEqual(email.subject, subject)
            return email.body

        email_id = None
        start = time.time()
        inbox = poplib.POP3_SSL('pop.mail.yahoo.com')
        try:
            inbox.user(test_email)
            inbox.pass_(os.environ['YAHOO_PASSWORD'])
            while time.time() - start < 60:
                # get 10 newest messages
                count, _ = inbox.stat()
                for i in reversed(range(max(1, count - 10), count + 1)):
                    print('getting msg', i)
                    _, lines, __ = inbox.retr(i)
                    lines = [l.decode('utf8') for l in lines]
                    if f'Subject: {subject}' in lines:
                        email_id = i
                        body = '\n'.join(lines)
                        return body
                time.sleep(5)
        finally:
            if email_id:
                inbox.dele(email_id)
            inbox.quit()

    against_staging = False

    def test_can_share_a_list_with_another_user(self):
        # Edith is a logged-in user
        test_email = 'edith@example.com'
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('email').send_keys(test_email)
        self.browser.find_element_by_name('email').send_keys(Keys.ENTER)

        # A message appears telling her an email has been sent
        self.wait_for(lambda: self.assertIn(
            'Check your email',
            self.browser.find_element_by_tag_name('body').text
        ))

        # She checks her email and finds a message
        body = self.wait_for_email(test_email, SUBJECT, 0)

        # It has a url link in it
        self.assertIn('Use this link to log in', body)
        url_search = re.search(r'http://.+/.+$', body)
        if not url_search:
            self.fail(f'Could not find url in email body:\n{body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # she clicks it
        self.browser.get(url)

        # She is logged in!
        self.wait_to_be_logged_in(email=test_email)
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))

        # Her friend Oniciferous is also hanging out on the lists site

        oni_browser = webdriver.Firefox()
        self.browser = oni_browser
        test_email = 'oniferous@example.com'
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('email').send_keys(test_email)
        self.browser.find_element_by_name('email').send_keys(Keys.ENTER)

        # A message appears telling her an email has been sent
        self.wait_for(lambda: self.assertIn(
            'Check your email',
            self.browser.find_element_by_tag_name('body').text
        ))

        # She checks her email and finds a message
        body = self.wait_for_email(test_email, SUBJECT, 1)

        # It has a url link in it
        self.assertIn('Use this link to log in', body)
        url_search = re.search(r'http://.+/.+$', body)
        if not url_search:
            self.fail(f'Could not find url in email body:\n{body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # she clicks it
        self.browser.get(url)

        # She is logged in!
        self.wait_to_be_logged_in(email=test_email)
        self.addCleanup(lambda: quit_if_possible(oni_browser))

        # Edith goes to the home page and starts a list
        self.browser = edith_browser
        list_page = ListPage(self).add_list_item('Get Help')
        # She notices a "Share this list" option
        share_box = list_page.get_share_box()
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your-friend@example.com'
        )

        #She shares her list.
        #The page updates to say that it is shared with Oniciferous:
        list_page.share_list_with('oniciferous@example.com')

        #Oniferous now goes to the lists page with his browser
        self.browser = oni_browser
        time.sleep(5)
        MyListsPage(self).go_to_my_lists_page()

        #He sees Edith's list in there!
        self.browser.find_element_by_link_text('Get Help').click()

        # On the list page, Oniciferous can see that it is Edith's list
        self.wait_for(lambda: self.assertEqual(
            list_page.get_list_owner(),
            'edith@example.com'
        ))

        # He adds an item to the list
        list_page.add_list_item('Hi Edith!')

        # When Edith refreshes the page, she sees Onificerous's addition
        self.browser = edith.browser
        self.browser.refresh()
        list_page.wait_for_row_in_list_table('Hi Edith!', 2)
