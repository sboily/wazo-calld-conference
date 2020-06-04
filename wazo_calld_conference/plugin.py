# -*- coding: utf-8 -*-
# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo.pubsub import CallbackCollector
from wazo_amid_client import Client as AmidClient

from .resources import (
    ConferencesResource,
    ConferenceResource,
    ConferenceResourceVerify,
    ConferencesAdhocResource,
    ConferenceAdhocResource,
    ConferenceParticipantAdhocResource,
    )
from .services import ConferenceService
from .stasis import ConferenceAdhocStasis
from .bus_consume import ConferencesBusEventHandler


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        ari = dependencies['ari']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        bus_consumer = dependencies['bus_consumer']
        bus_publisher = dependencies['bus_publisher']

        amid_client = AmidClient(**config['amid'])

        token_changed_subscribe(amid_client.set_token)

        conferences_service = ConferenceService(amid_client, ari.client)

        conferences_bus_event_handler = ConferencesBusEventHandler(bus_publisher)
        conferences_bus_event_handler.subscribe(bus_consumer)

        stasis = ConferenceAdhocStasis(ari, conferences_service)

        startup_callback_collector = CallbackCollector()
        ari.client_initialized_subscribe(startup_callback_collector.new_source())
        startup_callback_collector.subscribe(stasis.initialize)

        api.add_resource(ConferencesResource, '/conferences', resource_class_args=[conferences_service])
        api.add_resource(ConferenceResource, '/conferences/<conference_id>', resource_class_args=[conferences_service])
        api.add_resource(ConferenceResourceVerify, '/conferences/verify/<conference_id>', resource_class_args=[conferences_service])
        api.add_resource(ConferencesAdhocResource, '/conferences/adhoc', resource_class_args=[conferences_service])
        api.add_resource(ConferenceAdhocResource, '/conferences/adhoc/<conference_id>', resource_class_args=[conferences_service])
        api.add_resource(ConferenceParticipantAdhocResource, '/conferences/adhoc/<conference_id>/calls/<call_id>', resource_class_args=[conferences_service])
