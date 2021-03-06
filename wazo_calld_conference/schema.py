# -*- coding: utf-8 -*-
# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import (
    fields,
    Schema,
)
from marshmallow.validate import Length

from wazo_calld.plugin_helpers.mallow import StrictDict


class ConferenceSchema(Schema):
    conference_id = fields.Str(validate=Length(min=1), required=True)
    locked = fields.Str(validate=Length(min=1))
    muted = fields.Str(validate=Length(min=1))
    marked = fields.Str(validate=Length(min=1))
    parties = fields.Integer()
    participants = fields.List(StrictDict(key_field=fields.String(required=True, validate=Length(min=1)),
                                          value_field=fields.String(required=True, validate=Length(min=1)),
                                          missing=dict))

    class Meta:
        strict = True


class ConferenceParticipantsSchema(Schema):
    callerid_name = fields.Str(validate=Length(min=1))
    callerid_num = fields.Str(validate=Length(min=1))
    muted = fields.Str(validate=Length(min=1))
    answered_time = fields.Str(validate=Length(min=1))
    admin = fields.Str(validate=Length(min=1))
    language = fields.Str(validate=Length(min=1))
    linkedid = fields.Str(validate=Length(min=1))
    channel = fields.Str(validate=Length(min=1))

    class Meta:
        strict = True


class ConferenceAdhocSchema(Schema):
    host_call_id = fields.Str(validate=Length(min=1), required=True)
    participant_call_ids = fields.List(fields.Str(validate=Length(min=1)), required=True)

    class Meta:
        strict = True


conference_schema = ConferenceSchema()
conference_participants_schema = ConferenceParticipantsSchema()
conference_adhoc_schema = ConferenceAdhocSchema()
