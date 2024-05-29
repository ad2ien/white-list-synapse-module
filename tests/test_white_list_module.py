import aiounittest

from tests import MockModuleApi
from white_list_module import EimisWhiteList


class EimisWhiteListTestClass(aiounittest.AsyncTestCase):
    def setUp(self):
        self.config = EimisWhiteList.parse_config(
            {
                "idp_id": "idp_id",
                "room_id": "room_id",
            }
        )
        self.module = EimisWhiteList(self.config, MockModuleApi())

    def test_get_last_content_no_content(self):

        result = self.module.get_last_content({})

        self.assertEqual(result, "")

    def test_get_last_content_message(self):
        real_life_content = {
            "msgtype": "m.text",
            "body": "## test experiment\nyvonnière",
            "format": "org.matrix.custom.html",
            "formatted_body": "<h2>test experiment</h2>\n<p>yvonnière</p>\n",
            "m.mentions": {},
        }
        result = self.module.get_last_content(real_life_content)

        self.assertEqual(result, "## test experiment\nyvonnière")

    def test_get_last_content_modified_message(self):
        real_life_content = {
            "msgtype": "m.text",
            "body": " * patapouf\npignolin\nroger\ntartanfion",
            "m.new_content": {
                "msgtype": "m.text",
                "body": "patapouf\npignolin\nroger\ntartanfion",
                "m.mentions": {},
            },
            "m.mentions": {},
            "m.relates_to": {
                "rel_type": "m.replace",
                "event_id": "$ChWXbbIpW-NUPca17PXdsTSxVAXAKGZeKEae3mcTjdI",
            },
        }
        result = self.module.get_last_content(real_life_content)

        self.assertEqual(result, "patapouf\npignolin\nroger\ntartanfion")
