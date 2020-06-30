# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

logger = logging.getLogger(__name__)


class ConferenceAdhocNotifier:

    def __init__(self, bus_producer):
        self._bus_producer = bus_producer

    def participant_left(self, conference_id, call_id, user_uuid):
        event = UserParticipantLeftConferenceAdhocEvent(conference_id, call_id, user_uuid)
        headers = {'user_uuid:{uuid}'.format(uuid=user_uuid): True}
        self._bus_producer.publish(event, headers=headers)


class UserParticipantLeftConferenceAdhocEvent:

    name = 'conference_adhoc_participant_left'
    routing_key = 'conferences.adhoc.{conference_id}.participant.left'
    required_acl = 'events.conferences.users.{user_uuid}.conference_adhoc_participant_left'

    def __init__(self, conference_id, call_id, user_uuid):
        self.required_acl = self.required_acl.format(user_uuid)
        self._body = {
            'conference_id': conference_id,
            'call_id': call_id
        }
        super(UserParticipantLeftConferenceAdhocEvent, self).__init__()

    def marshal(self):
        return self._body
