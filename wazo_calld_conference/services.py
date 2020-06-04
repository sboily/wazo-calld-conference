# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import uuid
import logging

from wazo_calld.plugin_helpers import ami
from wazo_calld.plugin_helpers.exceptions import WazoAmidError


logger = logging.getLogger(__name__)

class ConferenceService(object):

    def __init__(self, amid, ari):
        self.amid = amid
        self.ari = ari

    def list_conferences(self):
        confs = self.amid.action('confbridgelistrooms')
        cn = []
        for conf in confs:
            c = self._conference(conf)
            if c:
                cn.append(c)
        return cn

    def get_conference(self, conference_id):
        conf = self._find_conference(self.amid.action('confbridgelistrooms'), conference_id)
        if conf:
            conf['participants'] = self.get_participants(conference_id)
        return conf

    def check_conference(self, conference_id):
        conf = self._find_conference(self.amid.action('confbridgelistrooms'), conference_id)
        if conf:
            return True
        return False

    def get_participants(self, conference_id):
        members = self.amid.action('confbridgelist', {'conference': conference_id})
        p = []

        for member in members:
            if member.get('Conference') == conference_id:
                p.append(self._participant(member))

        return p

    def create_conference_adhoc(self, calls):
        conference_id = uuid.uuid4()
        for call in calls:
            try:
                channel_initiator = self.ari.channels.get(channelId=call['initiator_call_id'])
                channel = self.ari.channels.get(channelId=call['call_id'])
                ami.redirect(self.amid,
                             channel.json['name'],
                             context='conference_adhoc',
                             exten=str(conference_id),
                             extra_channel=channel_initiator.json['name'])
                channel_initiator = None
            except WazoAmidError as e:
                logger.exception('wazo-amid error: %s', e.__dict__)

        return conference_id

    def update_conference_adhoc(self, conference_id, calls):
        for call in calls:
            try:
                channel_initiator = self.ari.channels.get(channelId=call['initiator_call_id'])
                channel = self.ari.channels.get(channelId=call['call_id'])
                ami.redirect(self.amid,
                             channel.json['name'],
                             context='conference_adhoc',
                             exten=str(conference_id),
                             extra_channel=channel_initiator.json['name'])
                channel_initiator = None
            except WazoAmidError as e:
                logger.exception('wazo-amid error: %s', e.__dict__)

        return conference_id

    def join_bridge(self, channel_id, future_bridge_uuid):
        logger.info('%s is joining bridge %s', channel_id, future_bridge_uuid)

        try:
            self.ari.channels.answer(channelId=channel_id)
        except ARINotFound:
            logger.info('the answered (%s) left the call before being bridged')
            return

        bridges = [candidate for candidate in self.ari.bridges.list() if
                   candidate.json['id'] == future_bridge_uuid]
        if bridges:
            bridge = bridges[0]
            logger.info('Using bridge %s', bridge.id)
        else:
            bridge = self.ari.bridges.createWithId(
                type='mixing',
                bridgeId=future_bridge_uuid,
            )

        bridge.addChannel(channel=channel_id)

    def _conference(self, conf):
        if conf.get('Conference'):
            return {'conference_id': conf['Conference'],
                    'locked': conf['Locked'],
                    'marked': conf['Marked'],
                    'muted': conf['Muted'],
                    'parties': conf['Parties']}
        return {}

    def _find_conference(self, confs, conference_id):
        for conf in confs:
            c = self._conference(conf)
            if c and conference_id == c['conference_id']:
                return c

        return None

    def _participant(self, member):
        return {'callerid_name': member.get('CallerIDName'),
                'callerid_num': member.get('CallerIDNum'),
                'muted': member.get('Muted'),
                'answered_time': member.get('AnsweredTime'),
                'admin': member.get('Admin'),
                'language': member.get('Language'),
                'linkedid': member.get('LinkedID'),
                'channel': member.get('Channel')}
