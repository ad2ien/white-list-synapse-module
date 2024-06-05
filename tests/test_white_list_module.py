from unittest import mock

import aiounittest
from synapse.api.room_versions import RoomVersions
from synapse.events import EventBase, make_event_from_dict
from synapse.spam_checker_api import RegistrationBehaviour

from tests import MockModuleApi
from white_list_module import EimisWhiteList


def create_event(
    message: str,
    prev_event_id: EventBase = None,
) -> EventBase:
    return make_event_from_dict(
        {
            "room_id": "room_id",
            "type": "m.room.message",
            "state_key": "",
            "sender": "user_id",
            "content": {"body": message},
            "auth_events": [],
            "prev_events": [prev_event_id],
        },
        room_version=RoomVersions.V9,
    )


class EimisWhiteListGetLastContentTestClass(aiounittest.AsyncTestCase):
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


class EimisWhiteListFromContentTestClass(aiounittest.AsyncTestCase):
    def setUp(self):
        self.config = EimisWhiteList.parse_config(
            {
                "idp_id": "idp_id",
                "room_id": "room_id",
            }
        )
        self.module = EimisWhiteList(self.config, MockModuleApi())

    async def test_get_whitelist_from_content_no_event(self):

        self.module._api._store = mock.MagicMock()
        self.module._api._store.get_latest_event_ids_in_room = mock.AsyncMock(
            return_value=[]
        )

        result = await self.module.get_whitelist_from_content()

        self.module._api._store.get_latest_event_ids_in_room.assert_called_once_with(
            "room_id"
        )
        self.assertEqual(result, set())

    async def test_get_whitelist_from_content_one_event(self):

        event56 = create_event("##Some title\nYvonne")

        self.module._api._store = mock.MagicMock()
        self.module._api._store.get_latest_event_ids_in_room = mock.AsyncMock(
            return_value=["event56"]
        )
        self.module._api._store.get_event = mock.AsyncMock(return_value=event56)

        result = await self.module.get_whitelist_from_content()

        self.module._api._store.get_latest_event_ids_in_room.assert_called_once_with(
            "room_id"
        )
        self.module._api._store.get_event.assert_called_once_with(
            "event56", allow_none=True
        )
        self.assertTrue("yvonne" in result)

    async def test_get_whitelist_from_content_several_events(self):

        event56 = create_event("##Some title\nYvonne")
        event57 = create_event("##Experiment 2\nPotiron\nGlandine", event56)

        self.module._api._store = mock.MagicMock()
        self.module._api._store.get_latest_event_ids_in_room = mock.AsyncMock(
            return_value=["event57"]
        )
        self.module._api._store.get_event = mock.AsyncMock(
            side_effect=[event57, event56]
        )

        result = await self.module.get_whitelist_from_content()

        self.module._api._store.get_latest_event_ids_in_room.assert_called_once_with(
            "room_id"
        )
        self.module._api._store.get_event.assert_any_call("event57", allow_none=True)
        # self.module._api._store.get_event.assert_any_call('event56', allow_none=True)
        self.assertTrue("yvonne" in result)
        self.assertTrue("potiron" in result)
        self.assertTrue("glandine" in result)

    async def test_check_registration_whitelist_other_idp(self):

        result = await self.module.check_registration_whitelist(
            None, "yvonne", [], "not_idp"
        )
        self.assertEqual(result, RegistrationBehaviour.ALLOW)

    async def test_check_registration_whitelist_no_idp(self):
        config = EimisWhiteList.parse_config(
            {
                "idp_id": "",
                "room_id": "room_id",
            }
        )
        module = EimisWhiteList(config, MockModuleApi())

        result = await module.check_registration_whitelist(
            None, "yvonne", [], "not_idp"
        )
        self.assertEqual(result, RegistrationBehaviour.ALLOW)


def test_parse_config():
    config = EimisWhiteList.parse_config(
        {
            "idp_id": "idp_id",
            "room_id": "room_id",
        }
    )

    assert config.idp_id == "oidc-idp_id"
    assert config.room_id == "room_id"
