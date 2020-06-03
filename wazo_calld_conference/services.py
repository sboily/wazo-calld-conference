# -*- coding: utf-8 -*-
# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random

from wazo_calld.plugin_helpers import ami
from wazo_calld.plugin_helpers.exceptions import WazoAmidError


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

    def create_conference_adhoc(self, initiator, calls):
        conference_room = ''.join(str(random.randint(0,9)) for _ in iter(range(12)))
        channel_initiator = self.ari.channels.get(channelId=initiator)
        for call in calls:
            try:
                channel = self.ari.channels.get(channelId=call)
                ami.redirect(self.amid,
                             channel.json['name'],
                             context='conference_adhoc',
                             exten=str(conference_room),
                             extra_channel=channel_initiator.json['name'])
                channel_initiator = None
            except WazoAmidError as e:
                logger.exception('wazo-amid error: %s', e.__dict__)

        return conference_room

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
