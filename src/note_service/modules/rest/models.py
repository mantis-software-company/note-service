import uuid

from note_service.database import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils import ScalarListType


class NotesModel(db.Model):
    __tablename__ = 'notes'
    __table_args__ = {'extend_existing': True}
    id = db.Column(UUIDType(binary=False), primary_key=True)
    tag = db.Column(ScalarListType(str))
    note_info = db.Column(db.Text)
    attachments = db.relationship("AttachmentsModel", back_populates="note", cascade="all, delete-orphan")
    created_date = db.Column(db.TIMESTAMP)
    updated_date = db.Column(db.TIMESTAMP)
    created_by = db.Column(db.String)
    updated_by = db.Column(db.String)

    def __init__(self, tag, note_info, attachments=None, created_date=None, updated_date=None,
                 created_by=None, updated_by=None):
        if attachments is None:
            attachments = []
        self.id = uuid.uuid4()
        self.tag = tag
        self.note_info = note_info
        self.attachments = attachments
        self.created_date = created_date
        self.updated_date = updated_date
        self.created_by = created_by
        self.updated_by = updated_by

    @hybrid_property
    def has_attachment(self):
        return bool(self.attachments)

    def __repr__(self):
        return '<Note %r>' % self.id


class AttachmentsModel(db.Model):
    __tablename__ = 'attachments'
    __table_args__ = {'extend_existing': True}
    id = db.Column(UUIDType(binary=False), primary_key=True)
    note_id = db.Column(UUIDType(binary=False), db.ForeignKey('notes.id'))
    note = db.relationship("NotesModel", back_populates="attachments",  cascade="save-update, merge, refresh-expire")
    attachment_file_key = db.Column(db.String)
    attachment_mime_type = db.Column(db.String)
    attachment_file_name = db.Column(db.String)

    def __init__(self, attachment_file_key, attachment_mime_type, attachment_file_name):
        self.id = uuid.uuid4()
        self.attachment_file_key = str(attachment_file_key)
        self.attachment_mime_type = attachment_mime_type
        self.attachment_file_name = attachment_file_name
