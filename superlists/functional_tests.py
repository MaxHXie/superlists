from selenium import webdriver
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
        self.fail('Finish the test!')

        # She is invited to enter a to-do item straight away

if __name__ == '__main__':
    unittest.main(warnings='ignore')

    #Tests are organized into classes, which inherit from unittest.TestCase

    #The main body of the test is in a method called test_can_start_a_list_and_retrieve_it_later. Any method whose name start starts test is a test method, and will be run by the test runner. You can have more than one test_ method per class. Nice descriptive names for our test methods are a good idea too.

    #setUp and tearDown are special methods which get run before and after each testselfself.
    #tearDown will run even if there is an error in the test. So, no more firefox windows lying around!

# Man vet inte om de gjort fel, fuskbygge etc.

# Work progress:
# 1. Write a functional test
# 2. Write unit test
# 3. Write application code and solve the unittests
# 4. Rerun functional tests to see if they pass
