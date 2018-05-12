# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_amid_client import Client as AmidClient
from xivo_auth_client import Client as AuthClient

from .resources import (
    ConferencesResource,
    ConferenceResource,
    ConferenceRecordResource,
    ConferenceParticipantsMuteResource,
    ConferenceParticipantsUnmuteResource,
    ConferenceParticipantsKickResource
    )
from .services import ConferenceService
from .bus_consume import ConferencesBusEventHandler


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        bus_publisher = dependencies['bus_publisher']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        bus_consumer = dependencies['bus_consumer']
        bus_publisher = dependencies['bus_publisher']

        amid_client = AmidClient(**config['amid'])

        token_changed_subscribe(amid_client.set_token)

        conferences_service = ConferenceService(amid_client)

        conferences_bus_event_handler = ConferencesBusEventHandler(bus_publisher)
        conferences_bus_event_handler.subscribe(bus_consumer)

        api.add_resource(ConferencesResource, '/conferences', resource_class_args=[conferences_service])
        api.add_resource(ConferenceResource, '/conferences/<conference_id>', resource_class_args=[conferences_service])
        api.add_resource(ConferenceRecordResource, '/conferences/<conference_id>/record', resource_class_args=[conferences_service])
        api.add_resource(ConferenceParticipantsMuteResource, '/conferences/<conference_id>/<channel>/mute', resource_class_args=[conferences_service])
        api.add_resource(ConferenceParticipantsUnmuteResource, '/conferences/<conference_id>/<channel>/unmute', resource_class_args=[conferences_service])
        api.add_resource(ConferenceParticipantsKickResource, '/conferences/<conference_id>/<channel>/kick', resource_class_args=[conferences_service])
