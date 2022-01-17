import uuid

from note_service.database import db
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils import ScalarListType


class Notes(db.Model):
    id = db.Column(UUIDType(binary=False), primary_key=True)
    tag = db.Column(ScalarListType(str))
    note_info = db.Column(db.Text)
    has_attachment = db.Column(db.Boolean)
    attachment_file_key = db.Column(db.String)
    created_date = db.Column(db.TIMESTAMP)
    updated_date = db.Column(db.TIMESTAMP)
    created_by = db.Column(db.String)
    updated_by = db.Column(db.String)

    def __init__(self, tag, note_info, has_attachment, attachment_file_key, created_date=None, updated_date=None,
                 created_by=None, updated_by=None):
        self.id = uuid.uuid4()
        self.tag = tag
        self.note_info = note_info
        self.has_attachment = has_attachment
        self.attachment_file_key = attachment_file_key
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_by = created_by
        self.updated_by = updated_by

    def __repr__(self):
        return '<Note %r>' % self.id
