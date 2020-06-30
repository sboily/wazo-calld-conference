# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

logger = logging.getLogger(__name__)


class ConferenceAdhocNotifier:

    def __init__(self, bus_producer):
        self._bus_producer = bus_producer

    def participant_left(self, conference_id, call_id, user_uuid):
        event = UserParticipantLeftConferenceAdhocEvent(conference_id, call_id)
        headers = {'user_uuid': user_uuid}
        self._bus_producer.publish(event, headers=headers)


class UserParticipantLeftConferenceAdhocEvent:

    name = 'conference_adhoc_participant_left'
    routing_key = 'conferences.adhoc.participant.left'
    required_acl = 'events.conferences.users.me.conference_adhoc_participant_left'

    def __init__(self, conference_id, call_id):
        self._body = {
            'conference_id': conference_id,
            'call_id': call_id
        }

    def marshal(self):
        return self._body
