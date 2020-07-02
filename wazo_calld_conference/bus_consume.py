# -*- coding: utf-8 -*-
# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from ari.exceptions import ARINotFound
from xivo_bus.resources.common.event import ArbitraryEvent


logger = logging.getLogger(__name__)


class ConferencesBusEventHandler(object):

    def __init__(self, ari, bus_publisher):
        self.ari = ari
        self.bus_publisher = bus_publisher

    def subscribe(self, bus_consumer):
        bus_consumer.on_ami_event('ConfbridgeStart', self._confbridge_start)
        bus_consumer.on_ami_event('ConfbridgeEnd', self._confbridge_end)
        bus_consumer.on_ami_event('BridgeEnter', self._relay_channel_entered_bridge)
        bus_consumer.on_ami_event('BridgeLeave', self._relay_channel_left_bridge)

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

    def _relay_channel_entered_bridge(self, event):
        channel_id = event['Uniqueid']
        bridge_id = event['BridgeUniqueid']
        logger.debug('Relaying to bus: channel %s entered bridge %s', channel_id, bridge_id)
        if int(event['BridgeNumChannels']) == 1:
            logger.debug('ignoring channel %s entered bridge %s: channel is alone', channel_id, bridge_id)
            return

        try:
            participant_channel_ids = self.ari.bridges.get(bridgeId=bridge_id).json['channels']
        except ARINotFound:
            logger.debug('bridge %s not found', bridge_id)
            return

        for participant_channel_id in participant_channel_ids:
            try:
                channel = self.ari.channels.get(channelId=participant_channel_id)
            except ARINotFound:
                logger.debug('channel %s not found', participant_channel_id)
                return

            call = self.services.make_call_from_channel(self.ari, channel)
            self.notifier.call_updated(call)

    def _relay_channel_left_bridge(self, event):
        channel_id = event['Uniqueid']
        bridge_id = event['BridgeUniqueid']
        if int(event['BridgeNumChannels']) == 0:
            logger.debug('ignoring channel %s left bridge %s: bridge is empty', channel_id, bridge_id)
            return

        logger.debug('Relaying to bus: channel %s left bridge %s', channel_id, bridge_id)

        try:
            participant_channel_ids = self.ari.bridges.get(bridgeId=bridge_id).json['channels']
        except ARINotFound:
            logger.debug('bridge %s not found', bridge_id)
            return

        for participant_channel_id in participant_channel_ids:
            try:
                channel = self.ari.channels.get(channelId=participant_channel_id)
            except ARINotFound:
                logger.debug('channel %s not found', participant_channel_id)
                return

            call = self.services.make_call_from_channel(self.ari, channel)
            self.notifier.call_updated(call)
