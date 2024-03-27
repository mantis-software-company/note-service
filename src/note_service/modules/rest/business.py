import io
import traceback
import uuid
from datetime import datetime
from http import HTTPStatus

import requests as requests
from flask import current_app
from flask_smorest import abort
from note_service.database import db
from note_service.modules.rest.models import NotesModel, AttachmentsModel
from note_service.modules.rest.utils import ResponseObject, PaginationObject
from sqlalchemy import func, column
from sqlalchemy.orm.exc import NoResultFound


def create_note(args, username):
    tag = args.get('tag')
    note_info = args.get('note_info')
    _attachments = args.get('attachments')

    if _attachments:
        attachments = [AttachmentsModel(attachment_file_key=_attachment.get("attachment_file_key"),
                                        attachment_mime_type=_attachment.get("attachment_mime_type")) for _attachment in
                       _attachments]
    else:
        attachments = None

    try:
        note = NotesModel(tag=tag, note_info=note_info, attachments=attachments,
                          created_date=datetime.now(), created_by=username)
        db.session.add(note)
    except Exception as e:
        db.session.rollback()
        tb = traceback.format_exc()
        return abort(HTTPStatus.BAD_GATEWAY, message="Note couldn't created.", messages=tb, exc=e)
    db.session.commit()
    db.session.refresh(note)
    return ResponseObject(data={"id": note.id}, message="Note successfully created.", status=HTTPStatus.OK)


def search_notes(args, pagination_parameters):
    tag = args.get("tag")
    note_info = args.get("note_info")
    _response = NotesModel.query
    _response = _response.select_from(func.unnest(func.string_to_array(NotesModel.tag, ',')).alias("tags")).filter(
        column("tags").like(tag))
    if note_info:
        _response = _response.filter(NotesModel.note_info.ilike("%" + note_info + "%"))
    _response = _response.distinct().order_by(NotesModel.created_date.desc()).paginate(pagination_parameters.page,
                                                                                       pagination_parameters.page_size)
    pagination_parameters.item_count = _response.total
    return ResponseObject(data=_response.items,
                          page=PaginationObject(page=_response.page, total_pages=_response.pages,
                                                total=_response.total),
                          status=HTTPStatus.OK)


def search_item_count(args):
    tag = args.get("tag")
    note_info = args.get("note_info")
    _response = NotesModel.query
    _response = _response.select_from(func.unnest(func.string_to_array(NotesModel.tag, ',')).alias("tags")).filter(
        column("tags").like(tag))
    if note_info:
        _response = _response.filter(NotesModel.note_info.ilike("%" + note_info + "%"))
    _response = _response.distinct()

    return ResponseObject(data={"count": str(_response.count())}, status=HTTPStatus.OK)


def fetch_note(note_id):
    try:
        _response = NotesModel.query.filter(NotesModel.id == note_id).one()
    except NoResultFound as e:
        abort(HTTPStatus.NOT_FOUND, message="Note not found.", exc=e)
    return ResponseObject(data=_response, status=HTTPStatus.OK)


def update_note(args, note_id, username):
    try:
        note = NotesModel.query.filter(NotesModel.id == note_id).one()
    except NoResultFound as e:
        abort(HTTPStatus.NOT_FOUND, message="Note not found.", exc=e)

    try:
        tag = args.get("tag")
        note_info = args.get("note_info")
        note.tag = tag
        note.note_info = note_info
        note.updated_date = datetime.now()
        note.updated_by = username
        db.session.add(note)
        db.session.commit()
    except Exception as e:
        tb = traceback.format_exc()
        abort(HTTPStatus.BAD_GATEWAY, message="Note couldn't updated.", messages=tb, exc=e)

    return ResponseObject(message="Note successfully updated.", status=HTTPStatus.OK)


def delete_note(note_id):
    try:
        note = NotesModel.query.filter(NotesModel.id == note_id).one()
    except NoResultFound as e:
        abort(HTTPStatus.NOT_FOUND, message="Note not found.", exc=e)

    try:
        db.session.delete(note)
        db.session.commit()
    except Exception as e:
        abort(HTTPStatus.BAD_GATEWAY, message="Note couldn't deleted.", exc=e)

    return ResponseObject(message="Note successfully deleted.", status=HTTPStatus.OK)


def get_file_url(note_id):
    try:
        note = NotesModel.query.filter(NotesModel.id == note_id).one()
    except NoResultFound as e:
        abort(HTTPStatus.NOT_FOUND, message="Note not found.", exc=e)
    pass

    if not note.has_attachment:
        abort(HTTPStatus.NOT_FOUND, message="Note has no attachment.")

    file_service_download_url = current_app.config.get('FILE_SERVICE_DOWNLOAD_URL')

    urls = [{attachment.attachment_file_key: f'{file_service_download_url}/{attachment.attachment_file_key}?contentDisposition=inline&contentType={attachment.attachment_mime_type}'} for attachment in note.attachments]

    return ResponseObject(data={"urls": urls}, status=HTTPStatus.OK)


def upload_attachment_file(files):
    attachment = files['attachment']
    f = io.BytesIO(attachment.stream.read())
    file_service_upload_url = current_app.config.get('FILE_SERVICE_UPLOAD_URL')
    r = requests.post(file_service_upload_url, files={"file": (attachment.filename, f, attachment.mimetype)})
    attachment_file_key = r.json()["key"]
    attachment_mime_type = attachment.mimetype
    return ResponseObject(
        data={"attachment_file_key": attachment_file_key, "attachment_mime_type": attachment_mime_type},
        status=HTTPStatus.CREATED)


def delete_attachment(note_id, attachment_file_key):
    try:
        attachment = (AttachmentsModel.query
                      .filter(AttachmentsModel.attachment_file_key == str(attachment_file_key))
                      .filter(AttachmentsModel.note_id == note_id).one())
    except NoResultFound as e:
        abort(HTTPStatus.NOT_FOUND, message="Note attachment not found.", exc=e)

    try:
        db.session.delete(attachment)
        db.session.commit()
    except Exception as e:
        abort(HTTPStatus.BAD_GATEWAY, message="Attachment couldn't deleted.", exc=e)

    return ResponseObject(message="Attachment successfully deleted.", status=HTTPStatus.OK)