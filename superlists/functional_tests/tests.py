from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time
import os

'''
We will use a constant called MAX_WAIT to set the maximum amount of time we're prepared
to wait. 10 seconds should be more than enough to catch any glitches or random slowness.
'''
MAX_WAIT = 10

#Setting LiveServerTestCase makes it run on its own database from scratch
class NewVisitorTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        '''
        The way I decided to do it is using an environment variable called
        STAGING_SERVER
        '''
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            '''
            Here's the hack: we replace self.live_server_url with the address of our
            "real server."
            '''
            self.live_server_url = 'http://' + staging_server

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def test_can_start_a_list_for_one_user(self):
        #Edith has heard about a cool new online to-do app. She goes
        #to check out its homepage
        #self.live_server_url = 'http://localhost:8000'
        self.browser.get(self.live_server_url)

        #She notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        #She is invited to enter a to-do item straight away
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        #She types "Buy peacock feathers" into a text box (Edith's hobby
        #is tying fly-fishing lures)
        inputbox.send_keys('Buy peacock feathers')

        #When she hits enter, the page updates, and now the page lists
        #"1: Buy peacock feathers" as an item in a to-do list table
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy peacock feathers")

        #There is still a text box inviting her to add another item. She
        #enters "Use peacock feathers to make a fly" (Edith is very
        #methodological)

        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys("Use peacock feathers to make a fly")
        inputbox.send_keys(Keys.ENTER)

        #The page updates again, and now shows both items on her list
        self.wait_for_row_in_list_table("1: Buy peacock feathers")
        self.wait_for_row_in_list_table("2: Use peacock feathers to make a fly")

        #Satisfied, the goes back to sleep

    def test_multiple_users_can_start_lists_at_different_urls(self):
        #Edith starts a new to-do list
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        #She notices that her list has a unique URL
        edith_list_url = self.browser.current_url
        #assertRegex is a helper function from unittest that checks whther a string
        #matches a regular expression. We use it to check that our new REST-ish design
        #has been implemented. Find our more in the unittest documentation.
        self.assertRegex(edith_list_url, '/lists/.+')

        #Next we imagine a new user coming along. We want to check that they don't see
        #any of Edith's items when they visit the home page, and that they get their own unique
        #URL for their list:

        #Now a new user, Francis, comes along to the site.

        '''
        I am using the convention of double hashes (##) to indicate "meta-comments" -
        comments about how the test is working and why - so that we can distinguich them
        from regular comments in FTs which explain the User Story. They're a message to our
        future selves, which might otherwise be wondering why the heck we're quitting the browser
        and starting a new one...
        '''

        ##We use a new browser to make sure that no information
        ##of Edith's is coming through from cookies etc
        self.browser.quit()
        self.browser = webdriver.Firefox()

        #Francis visits the home page. There is no sign of Edith's list
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn("Buy peacock feathers", page_text)
        self.assertNotIn("make a fly", page_text)

        #Francis starts a new list by entering a new item. He is less interesting than Edith...
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys("Buy milk")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        #Francis gets his own unique URL
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        #Again, there is on trace of Edith's list
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertIn('Buy milk', page_text)

        #Satisfied, they both fo to sleep

    def test_layout_and_styling(self):
        #Edith goes to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        #She notices tha input box is nice and centered
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )

        #She starts a new list and sees the input is nicely
        #centered there too
        inputbox.send_keys('testing')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: testing')
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )

'''
Where are we with our own to-do list?
    - Adjust model so that items are associated with different lists.
    - Add unique URLS for each list...
    - Add a URL for creating a new list via POST
    - Add URLs for adding a new item to an existing list via POST
    - Last step until we get an MVP
'''
