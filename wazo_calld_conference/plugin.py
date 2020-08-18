# -*- coding: utf-8 -*-
# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo.pubsub import CallbackCollector
from wazo_amid_client import Client as AmidClient
from wazo_confd_client import Client as ConfdClient
from wazo_calld.phoned import PhonedClient

from wazo_calld.plugins.calls.notifier import CallNotifier
from wazo_calld.plugins.calls.services import CallsService
from wazo_calld.plugins.calls.dial_echo import DialEchoManager

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
from .notifier import ConferenceAdhocNotifier


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

        notifier = ConferenceAdhocNotifier(bus_publisher)

        confd_client = ConfdClient(**config['confd'])
        
        phoned_client = PhonedClient(**config['phoned'])

        token_changed_subscribe(confd_client.set_token)

        dial_echo_manager = DialEchoManager()

        calls_notifier = CallNotifier(bus_publisher)
        calls_service = CallsService(amid_client, config['ari']['connection'], ari.client, confd_client, dial_echo_manager, phoned_client, calls_notifier)

        conferences_service = ConferenceService(amid_client, ari.client, notifier)

        conferences_bus_event_handler = ConferencesBusEventHandler(ari.client, bus_publisher, calls_service, calls_notifier)
        conferences_bus_event_handler.subscribe(bus_consumer)

        stasis = ConferenceAdhocStasis(ari, conferences_service, notifier)

        startup_callback_collector = CallbackCollector()
        ari.client_initialized_subscribe(startup_callback_collector.new_source())
        startup_callback_collector.subscribe(stasis.initialize)

        api.add_resource(ConferencesResource, '/conferences', resource_class_args=[conferences_service])
        api.add_resource(ConferenceResource, '/conferences/<conference_id>', resource_class_args=[conferences_service])
        api.add_resource(ConferenceResourceVerify, '/conferences/verify/<conference_id>', resource_class_args=[conferences_service])
        api.add_resource(ConferencesAdhocResource, '/users/me/conferences/adhoc', resource_class_args=[conferences_service])
        api.add_resource(ConferenceAdhocResource, '/users/me/conferences/adhoc/<conference_id>', resource_class_args=[conferences_service])
        api.add_resource(ConferenceParticipantAdhocResource, '/users/me/conferences/adhoc/<conference_id>/participants/<call_id>', resource_class_args=[conferences_service])
