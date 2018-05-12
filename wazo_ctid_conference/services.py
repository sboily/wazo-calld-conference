# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging


class ConferenceService(object):

    def __init__(self, amid):
        self.amid = amid

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

    def get_participants(self, conference_id):
        members = self.amid.action('confbridgelist', {'conference': conference_id})
        p = []

        for member in members:
            if member.get('Conference') == conference_id:
                p.append(self._participant(member))

        return p


    def mute(self, conference_id, channel):
        return self.amid.action('ConfbridgeMute', {'Conference': conference_id, 'Channel': channel})

    def unmute(self, conference_id, channel):
        return self.amid.action('ConfbridgeUnmute', {'Conference': conference_id, 'Channel': channel})

    def kick(self, conference_id, channel):
        return self.amid.action('ConfBridgeKick', {'Conference': conference_id, 'Channel': channel})

    def start_record(self, conference_id, record_file):
        return self.amid.action('ConfBridgeStartRecord', {'Conference': conference_id, 'RecordFile': record_file})

    def stop_record(self, conference_id):
        return self.amid.action('ConfBridgeStopRecord', {'Conference': conference_id})

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
