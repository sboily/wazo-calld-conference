# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

logger = logging.getLogger(__name__)


class ConferenceAdhocStasis:

    _app_name = 'adhoc'

    def __init__(self, ari, service, notifier):
        self._core_ari = ari
        self._ari = ari.client
        self._service = service
        self._notifier = notifier

    def stasis_start(self, event_object, event):
        if event['application'] != self._app_name:
            return

        args = event['args']
        if len(args) < 1:
            logger.info('%s called without enough arguments %s', self._app_name, args)
            return

        future_bridge_uuid = args[0]
        channel_id = event['channel']['id']
        logger.debug('conference adhoc: %s channel_id: %s', future_bridge_uuid, channel_id)

        self._service.join_bridge(channel_id, future_bridge_uuid)

    def _add_ari_application(self):
        self._core_ari.register_application(self._app_name)
        self._core_ari.reload()

    def _subscribe(self):
        self._ari.on_channel_event('StasisStart', self.stasis_start)
        self._ari.on_channel_event('ChannelLeftBridge', self.on_hangup)

    def initialize(self):
        self._subscribe()
        self._add_ari_application()

    def on_hangup(self, channel, event):
        if event['application'] != self._app_name:
            return

        logger.debug('conference adhoc: participant channel_id: %s is left', channel_id)

        conference_id = event['bridge']['id']
        call_id = event['channel']['id']
        user_uuid = self._ari.bridges.getBridgeVar(bridgeId=conference_id, variable='CONF_ADHOC_OWNER').get('CONF_ADHOC_OWNER')

        self._notifier.participant_left(conference_id, call_id, user_uuid)
