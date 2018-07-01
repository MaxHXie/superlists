class MyListsPage(object):
    def __init__(self, test):
        self.test = test

    def go_to_my_lists_page(self):
        # It is possible to go to the "My lists"-page. Also there is a title saying "My Lists".
        self.test.browser.get(self.test.live_server_url)
        self.test.browser.find_element_by_link_text('My Lists').click()
        self.test.wait_for(lambda: self.test.assertEqual(
            self.test.browser.find_element_by_tag_name('h1').text,
            'My lists'
        ))
        return self
