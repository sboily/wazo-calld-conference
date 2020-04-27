# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_calld.auth import required_acl
from wazo_calld.http import AuthResource

from .schema import (
    conference_schema,
    conference_participants_schema
)


class ConferencesResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('calld.conferences.read')
    def get(self):
        conferences = self._conferences_service.list_conferences()

        return {
            'items': conference_schema.dump(conferences, many=True).data
        }, 200


class ConferenceResource(AuthResource):

    def __init__(self, conferences_service):
        self._conferences_service = conferences_service

    @required_acl('calld.conferences.{conference_id}.read')
    def get(self, conference_id):
        conference = self._conferences_service.get_conference(conference_id)

        return conference_schema.dump(conference).data
