# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import uuid
import logging
import requests

from ari.exceptions import ARINotFound

from wazo_calld.plugin_helpers import ami
from wazo_calld.plugin_helpers.exceptions import WazoAmidError


logger = logging.getLogger(__name__)


def ami_redirect_extra(amid, channel, context, exten, priority=1, extra_channel=None, extra_context=None, extra_exten=None, extra_priority=None):
    destination = {
        'Channel': channel,
        'Context': context,
        'Exten': exten,
        'Priority': priority,
    }
    if extra_channel:
        destination['ExtraChannel'] = extra_channel
    if extra_context:
        destination['ExtraContext'] = extra_context
    if extra_exten:
        destination['ExtraExten'] = extra_exten
        destination['ExtraPriority'] = extra_priority if extra_priority else 1
    try:
        amid.action('Redirect', destination)
    except requests.RequestException as e:
        raise WazoAmidError(amid, e)


class ConferenceService(object):

    def __init__(self, amid, ari, notifier):
        self.amid = amid
        self.ari = ari
        self.notifier = notifier

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

    def create_conference_adhoc(self, calls, user_uuid):
        conference_id = uuid.uuid4()
        conference_owner = None
        for call in calls:
            try:
                channel_initiator = self.ari.channels.get(channelId=call['initiator_call_id'])
                self.ari.channels.setChannelVar(channelId=call['initiator_call_id'], variable='CONF_ADHOC_OWNER', value=user_uuid, bypassStasis=True)
                channel = self.ari.channels.get(channelId=call['call_id'])
                if not conference_owner:
                    conference_owner = call['initiator_call_id']
                    ami_redirect_extra(self.amid,
                                       channel.json['name'],
                                       context='conference_adhoc',
                                       exten=str(conference_id),
                                       extra_channel=channel_initiator.json['name'])
                else:
                    ami_redirect_extra(self.amid,
                                       channel.json['name'],
                                       context='conference_adhoc',
                                       exten=str(conference_id),
                                       extra_channel=channel_initiator.json['name'],
                                       extra_context='conference_adhoc',
                                       extra_exten='h',
                                       extra_priority=1)
            except WazoAmidError as e:
                logger.exception('wazo-amid error: %s', e.__dict__)

        return {'conference_id': str(conference_id)}

    def update_conference_adhoc(self, conference_id, calls):
        for call in calls:
            try:
                channel_initiator = self.ari.channels.get(channelId=call['initiator_call_id'])
                channel = self.ari.channels.get(channelId=call['call_id'])
                ami_redirect_extra(self.amid,
                                   channel.json['name'],
                                   context='conference_adhoc',
                                   exten=str(conference_id),
                                   extra_channel=channel_initiator.json['name'])
                channel_initiator = None
            except WazoAmidError as e:
                logger.exception('wazo-amid error: %s', e.__dict__)

        return conference_id

    def delete_conference_adhoc(self, conference_id):
        bridge = self.ari.bridges.get(bridgeId=conference_id)
        
        if bridge:
            for channel in bridge.json['channels']:
                self.ari.channels.hangup(channelId=channel)
            bridge.destroy()
        return '', 204

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

        user_uuid = self.ari.channels.getChannelVar(variable='CONF_ADHOC_OWNER').get('value')
        bridge.setBridgeVar(variable='CONF_ADHOC_OWNER', value=user_uuid)
        bridge.addChannel(channel=channel_id)

    def remove_participant_conference_adhoc(self, conference_id, call_id, user_uuid):
        try:
            self.ari.channels.hangup(channelId=call_id)
            self.notifier.participant_left(conference_id, call_id, user_uuid)
        except ARINotFound:
            logger.info('Participant in conference adhoc does not exist')

        return ''

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
