# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import urllib

from xivo_ctid_ng.auth import required_acl
from xivo_ctid_ng.rest_api import AuthResource

from .schema import (
    conference_schema,
    conference_participants_schema
)


class ConferencesResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('ctid-ng.conferences.read')
    def get(self):
        conferences = self._conferences_service.list_conferences()

        return {
            'items': conference_schema.dump(conferences, many=True).data
        }, 200


class ConferenceResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('ctid-ng.conferences.{conference_id}.read')
    def get(self, conference_id):
        conference = self._conferences_service.get_conference(conference_id)

        return conference_schema.dump(conference).data


class ConferenceRecordResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('ctid-ng.conferences.{conference_id}.record.create')
    def post(self, conference_id):
        conference = self._conferences_service.start_record(conference_id, '/tmp/confbridge')

        return '', 201

    @required_acl('ctid-ng.conferences.{conference_id}.record.delete')
    def delete(self, conference_id):
        conference = self._conferences_service.stop_record(conference_id)

        return '', 204


class ConferenceParticipantsMuteResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('ctid-ng.conferences.{conference_id}.participants.mute.update')
    def put(self, conference_id, channel):
        conference = self._conferences_service.mute(conference_id, urllib.unquote(channel))

        return '', 204


class ConferenceParticipantsUnmuteResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('ctid-ng.conferences.{conference_id}.participants.unmute.update')
    def put(self, conference_id, channel):
        conference = self._conferences_service.unmute(conference_id, urllib.unquote(channel))

        return '', 204


class ConferenceParticipantsKickResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('ctid-ng.conferences.{conference_id}.participants.kick.update')
    def put(self, conference_id, channel):
        conference = self._conferences_service.kick(conference_id, urllib.unquote(channel))

        return '', 204
