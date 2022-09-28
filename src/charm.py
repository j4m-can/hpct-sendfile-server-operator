#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Sendfile server charm.
"""

import logging
import pathlib

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus

from hpctlib.interface import interface_registry

# load
import interfaces.sendfile

logger = logging.getLogger(__name__)


class HpctSendfileServerCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.start, self._on_start)

        self.framework.observe(
            self.on.sendfile_relation_changed, self._on_sendfile_relation_changed
        )

        self.framework.observe(self.on.send_file_action, self._on_send_file_action)
        self.framework.observe(self.on.show_file_action, self._on_show_file_action)

        self.siface = interface_registry.load("relation-unit-sendfile", self, "sendfile")

    def _on_config_changed(self, event):
        pass

    def _on_start(self, event):
        self.unit.status = ActiveStatus("ready")

    def _on_sendfile_relation_changed(self, event):
        server_iface = self.siface.select(self.unit)
        client_iface = self.siface.select(event.unit)

        if client_iface.nonce != "" and client_iface.nonce == server_iface.file.nonce:
            # reset
            # server_iface.file.clear()
            logger.debug("received acknowledgement, resetting nonce")
            server_iface.file.nonce = ""

    def _on_send_file_action(self, event):
        filename = event.params["filename"]
        p = pathlib.Path(filename)
        if not p.exists():
            event.log("file ({filename}) does not exist")
            return

        # check ok to update "file"
        server_iface = self.siface.select(self.unit)
        if server_iface.file.nonce != "":
            event.log("last sendfile not acknowleged")
            return

        # load file into local unit data
        server_iface.file.load(filename)
        logger.debug(f"loaded file ({filename}) nonce ({server_iface.file.nonce})")

    def _on_show_file_action(self, event):
        server_iface = self.siface.select(self.unit)
        logger.debug(
            f"*** loaded file ({server_iface.file.path}) nonce ({server_iface.file.nonce})"
        )


if __name__ == "__main__":
    main(HpctSendfileServerCharm)
