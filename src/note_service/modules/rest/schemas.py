from flask_smorest.fields import Upload
from marshmallow import Schema, fields, validate


class BaseResponse(Schema):
    data = fields.Dict()
    message = fields.String()
    statusCode = fields.String()
    exceptionDetail = fields.String()

    class Meta:
        ordered = True


class Pagination(Schema):
    page = fields.Integer()
    total_pages = fields.Integer()
    total = fields.Integer()


class Note(Schema):
    id = fields.UUID(dump_only=True)
    tag = fields.List(fields.String, required=True)
    note_info = fields.String(required=True, validate=validate.Length(min=2))
    has_attachment = fields.Boolean(dump_only=True)
    attachment_file_key = fields.UUID(dump_only=True)
    created_date = fields.DateTime(dump_only=True)
    updated_date = fields.DateTime(dump_only=True)
    created_by = fields.String(dump_only=True)
    updated_by = fields.String(dump_only=True)
    
    class Meta:
        exclude = ('attachment_file_key', )


class NoteSearch(Note):
    note_info = fields.String(required=False)
    tag = fields.String(required=True)


class NoteResponse(BaseResponse):
    data = fields.Nested(Note)
    page = fields.Nested(Pagination)


class NotesResponse(NoteResponse):
    data = fields.Nested(Note, many=True)


class NoteFile(Schema):
    attachment = Upload()
