from django.core.urlresolvers import resolve
from django.test import Client
from django.test import TestCase
import json

from osc.views import rest_api


class RestAPITest(TestCase):
    def test_api_altitude_resolves_to_api_page_view(self):
        found = resolve('/altitud/')
        self.assertEqual(found.func.view_class, rest_api.GoogleElevationList)

    def test_api_altitude_returns_correct_json(self):
        c = Client()
        response = c.get('/altitud/')
        json_response = response.content.decode('utf8')
        json.loads(json_response)
        # The test runner will catch all exceptions you didn't assert
        # would be raised, assertTrue() do nothing but ensures that didn't
        # forget an assertion
        self.assertTrue(True, "shouldn't throw exceptions")

    def test_api_altitude_returns_401_when_no_authentication_credentials(self):
        c = Client()
        response = c.get('/altitud/')
        self.assertTrue(response.status_code == 401,
                        "Status code should be 401 because authentication "
                        "credentials were not provided")
