# -*- coding: utf-8 -*-
# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from wazo_calld.auth import required_acl
from wazo_calld.http import AuthResource, ErrorCatchingResource

from .schema import (
    conference_schema,
    conference_participants_schema,
    conference_adhoc_schema,
)


class ConferencesResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('calld.conferences.read')
    def get(self):
        conferences = self._conferences_service.list_conferences()

        return {
            'items': conference_schema.dump(conferences, many=True)
        }, 200


class ConferenceResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('calld.conferences.{conference_id}.read')
    def get(self, conference_id):
        conference = self._conferences_service.get_conference(conference_id)

        return conference_schema.dump(conference)

class ConferenceResourceVerify(ErrorCatchingResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    def get(self, conference_id):
        conference = self._conferences_service.check_conference(conference_id)

        if not conference:
            return '', 404

        return '', 200


class ConferencesAdhocResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('calld.conferences.adhoc.create')
    def post(self):
        form = conference_adhoc_schema.load(request.get_json())
        conference_adhoc = self._conferences_service.create_conference_adhoc(**form)

        return conference_adhoc, 201


class ConferenceAdhocResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('calld.conferences.adhoc.{conference_id}.update')
    def put(self, conference_id):
        form = conference_adhoc_schema.load(request.get_json())
        conference_adhoc = self._conferences_service.update_conference_adhoc(conference_id, **form)

        return conference_adhoc_schema.dump(conference_adhoc), 204

    @required_acl('calld.conferences.adhoc.{conference_id}.delete')
    def delete(self, conference_id):
        conference_adhoc = self._conferences_service.delete_conference_adhoc(conference_id)
        return '', 204


class ConferenceParticipantAdhocResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('calld.conferences.adhoc.{conference_id}.{call_id}.delete')
    def delete(self, conference_id, call_id):
        self._conferences_service.remove_participant_conference_adhoc(conference_id, call_id)
        return '', 204
