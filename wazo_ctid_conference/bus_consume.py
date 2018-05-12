# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_bus.resources.common.event import ArbitraryEvent


logger = logging.getLogger(__name__)


class ConferencesBusEventHandler(object):

    def __init__(self, bus_publisher):
        self.bus_publisher = bus_publisher

    def subscribe(self, bus_consumer):
        bus_consumer.on_ami_event('ConfbridgeJoin', self._confbridge_join)
        bus_consumer.on_ami_event('ConfbridgeLeave', self._confbridge_leave)
        bus_consumer.on_ami_event('ConfbridgeStart', self._confbridge_start)
        bus_consumer.on_ami_event('ConfbridgeEnd', self._confbridge_end)
        bus_consumer.on_ami_event('ConfbridgeMute', self._confbridge_mute)
        bus_consumer.on_ami_event('ConfbridgeUnmute', self._confbridge_unmute)
        bus_consumer.on_ami_event('ConfbridgeRecord', self._confbridge_record)
        bus_consumer.on_ami_event('ConfbridgeStopRecord', self._confbridge_stoprecord)
        bus_consumer.on_ami_event('ConfbridgeTalking', self._confbridge_talking) # need talk_detection_events in confbridge configuration

    def _confbridge_join(self, event):
        bus_event = ArbitraryEvent(
            name='conference_join',
            body=event,
            required_acl='events.conferences'
        )
        bus_event.routing_key = 'conferences.join'
        self.bus_publisher.publish(bus_event)

    def _confbridge_leave(self, event):
        bus_event = ArbitraryEvent(
            name='conference_leave',
            body=dict(),
            required_acl='events.conferences'
        )
        bus_event.routing_key = 'conferences.leave'
        self.bus_publisher.publish(bus_event)

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

    def _confbridge_mute(self, event):
        bus_event = ArbitraryEvent(
            name='conference_mute',
            body=event,
            required_acl='events.conferences'
        )
        bus_event.routing_key = 'conferences.mute'
        self.bus_publisher.publish(bus_event)

    def _confbridge_unmute(self, event):
        bus_event = ArbitraryEvent(
            name='conference_unmute',
            body=event,
            required_acl='events.conferences'
        )
        bus_event.routing_key = 'conferences.unmute'
        self.bus_publisher.publish(bus_event)

    def _confbridge_record(self, event):
        bus_event = ArbitraryEvent(
            name='conference_record',
            body=event,
            required_acl='events.conferences'
        )
        bus_event.routing_key = 'conferences.record'
        self.bus_publisher.publish(bus_event)

    def _confbridge_stoprecord(self, event):
        bus_event = ArbitraryEvent(
            name='conference_stoprecord',
            body=event,
            required_acl='events.conferences'
        )
        bus_event.routing_key = 'conferences.stoprecord'
        self.bus_publisher.publish(bus_event)

    def _confbridge_talking(self, event):
        bus_event = ArbitraryEvent(
            name='conference_talking',
            body=event,
            required_acl='events.conferences'
        )
        bus_event.routing_key = 'conferences.talking'
        self.bus_publisher.publish(bus_event)
