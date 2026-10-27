import logging
from typing import Any, Collection, Dict, Optional, Set, Tuple

import attr
from synapse.module_api import ModuleApi
from synapse.spam_checker_api import RegistrationBehaviour

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True, frozen=True)
class EasyWhiteListConfig:
    idp_id: Optional[str] = None
    room_id: Optional[str] = None


class EasyWhiteList:
    def __init__(self, config: EasyWhiteListConfig, api: ModuleApi):
        logger.info("Init EasyWhiteList")

        self._api = api
        self._config = config

        self._api.register_spam_checker_callbacks(
            check_registration_for_spam=self.check_registration_whitelist,
        )

    @staticmethod
    def parse_config(config: Dict[str, Any]) -> EasyWhiteListConfig:
        """Instantiates a EasyWhiteListConfig

        Args:
            config: The raw configuration dict

        Returns:
            A EasyWhiteListConfig generated from this configuration
        """

        logger.info("Config EasyWhiteList")

        idp_id = config.get("idp_id")
        return EasyWhiteListConfig(
            idp_id="oidc-" + idp_id if idp_id else None,
            room_id=config.get("room_id", None),
        )

    async def check_registration_whitelist(
        self,
        email_threepid: Optional[dict],
        username: Optional[str],
        request_info: Collection[Tuple[str, str]],
        auth_provider_id: Optional[str] = None,
    ) -> RegistrationBehaviour:

        logger.info(
            "Check_registration_whitelist %s provider id: %s",
            username,
            auth_provider_id,
        )

        # not configured? don't get involved
        if not self._config.room_id:
            return RegistrationBehaviour.ALLOW

        # White list applies only to specified provider
        if auth_provider_id != self._config.idp_id:
            return RegistrationBehaviour.ALLOW

        whitelist = await self.get_whitelist_from_content()
        logger.debug("EasyWhitelist: " + str(whitelist))

        normalized_username = (username or "").strip().lower()
        return (
            RegistrationBehaviour.ALLOW
            if normalized_username in whitelist
            else RegistrationBehaviour.DENY
        )

    async def get_whitelist_from_content(self) -> Collection[str]:
        """Extracts the whitelist from the messages of a room

        Args:
            event: The event to extract the whitelist from

        Returns:
            A collection of user IDs to whitelist
        """
        whitelist: Set[str] = set()

        room_id = self._config.room_id
        if not room_id:
            return whitelist

        # Synapse's private store API; its type stubs are unreliable across
        # versions, so treat it as Any.
        store: Any = self._api._store
        last_events = await store.get_latest_event_ids_in_room(room_id)

        if not last_events or len(last_events) == 0:
            return whitelist

        event_id: Optional[str] = list(last_events)[0]

        while event_id:
            event = await store.get_event(event_id, allow_none=True)
            if event is None:
                break

            if event.type == "m.room.message":
                content = self.get_last_content(event.content)
                whitelist.update(
                    line.strip().lower()
                    for line in content.splitlines()
                    if line.strip()
                )

            if event.prev_event_ids():
                event_id = event.prev_event_ids()[0]
            else:
                event_id = None

        return whitelist

    def get_last_content(self, event_content) -> str:
        """Extracts the last content of a message in case this one has been edited

        Args:
            event: The event to extract the content from

        Returns:
            The content of the last message
        """
        while "m.new_content" in event_content:
            event_content = event_content["m.new_content"]

        if "body" not in event_content:
            return ""

        return event_content["body"]
