# -*- coding: utf-8 -*-
# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_bus.resources.common.event import ArbitraryEvent


logger = logging.getLogger(__name__)


class ConferencesBusEventHandler(object):

    def __init__(self, bus_publisher):
        self.bus_publisher = bus_publisher

    def subscribe(self, bus_consumer):
        bus_consumer.on_ami_event('ConfbridgeStart', self._confbridge_start)
        bus_consumer.on_ami_event('ConfbridgeEnd', self._confbridge_end)

    def _confbridge_start(self, event):
        bus_event = ArbitraryEvent(
            name='conference_start',
            body=event,
            required_acl='events.conferences'
        )
        bus_event.routing_key = 'conferences.join'
        self.bus_publisher.publish(bus_event)

    def _confbridge_end(self, event):
        bus_event = ArbitraryEvent(
            name='conference_end',
            body=event,
            required_acl='events.conferences'
        )
        bus_event.routing_key = 'conferences.end'
        self.bus_publisher.publish(bus_event)
