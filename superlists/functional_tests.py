from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import unittest

class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        #Edith has heard about a cool new online to-do app. She goes
        #to check out its homepage
        self.browser.get('http://localhost:8000')

        #She notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        #She is invited to enter a to-do item straight away
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('pladeholder'),
            'Enter a to-do item'
        )

        #She types "Buy peacock feathers" into a text box (Edith's hobby
        #is tying fly-fishing lures)
        inputbox.send_keys('Buy peacock feathers')

        #When she hits enter, the page updates, and now the page lists
        #"1: Buy peacock feathers" as an item in a to-do list table
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertTrue(
            any(row.text == '1: Buy peacock feathers' for row in rows)
        )

        #There is still a text box inviting her to add another item. She
        #enters "Use peacock feathers to make a fly" (Edith is very
        #methodological)
        self.fail('Finish the test!')

        #The page updates again, and now shows both items on her list


        # 1. We are using several of the methods that Selenium provides to examine web pages
        #find_element_by_tag_name, find_element_by_id and find_elements_by_tag_name (notice the extra s,
        #which means it will return several elements rather than just one.)

        #2. We also use send_keys, which is Selenium's way of typing into input elements.

        #3. The Keys class (don't forget ot import it) lets us send special keys like Enter?

        #4. When we hit Enter, the page will refresh. The time.sleep is there to make sure the browser
        #has finished loading before we make any assertiong about the new page. This is called an "explicit way"
        #(a very simple one; we'll improve it in Chapter 6)
