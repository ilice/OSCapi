from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
import unittest


class NewVisitorTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(NewVisitorTest, cls).setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(NewVisitorTest, cls).tearDownClass()

    def test_can_login_into_admin_pages_and_logout_later(self):
        # Teanocrata has heard about a cool new online app with an incredible
        # API. She goes to check the API.
        self.selenium.get('%s%s' % (self.live_server_url, '/'))

        # She notice the page title and header mention Open Smart Country API
        self.assertIn('Open Smart Country', self.selenium.title)

        # The page shows her a little explanation about the OSC REST api

        # She is invited to enter to Admin packages

        # When she clicks on Admin button, the page ask her for her credentials

        # She enters her name and password

        # The page updates and now shows OSC - Admin pages

        # Teanocrata wonders wheter the site will have many options. Then she
        # sees that there are plenty of it.

        # She log out from the page and then the page updates again, and shows
        # the little explanation about the OSC REST api again

        # Satisfied, she goes to sleep


if __name__ == '__main__':
    unittest.main()
