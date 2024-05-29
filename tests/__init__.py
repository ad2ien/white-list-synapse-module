from typing import Any

import attr


@attr.s(auto_attribs=True)
class MockModuleApi:
    """Mock of a synapse.module_api.ModuleApi, only implementing the methods the
    WhiteList module will use.
    """

    def register_spam_checker_callbacks(self, *args: Any, **kwargs: Any) -> None:
        """Don't fail when the module tries to register its callbacks."""
        pass
