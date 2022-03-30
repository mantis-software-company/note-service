import io
import traceback
from datetime import datetime
from http import HTTPStatus

import requests as requests
from flask import current_app
from flask_smorest import abort
from sqlalchemy import func, column
from sqlalchemy.orm.exc import NoResultFound


from note_service.database import db
from note_service.modules.rest.models import Notes
from note_service.modules.rest.utils import ResponseObject, PaginationObject


def create_note(files, args, username):
    tag = args.get('tag')
    note_info = args.get('note_info')
    note = Notes(tag, note_info, False, None, created_date=datetime.now(), created_by=username)
    db.session.add(note)
    if files:
        try:
            attachment = files['attachment']
            f = io.BytesIO(attachment.stream.read())
            file_service_upload_url = current_app.config.get('FILE_SERVICE_UPLOAD_URL')
            r = requests.post(file_service_upload_url, files={"file": (attachment.filename, f, attachment.mimetype)})
            attachment_file_key = r.json()["key"]
            note.has_attachment = True
            note.attachment_file_key = attachment_file_key
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
    _response = Notes.query
    _response = _response.select_from(func.unnest(func.string_to_array(Notes.tag, ',')).alias("tags")).filter(column("tags").like(tag))
    if note_info:
        _response = _response.filter(Notes.note_info.ilike("%" + note_info + "%"))
    _response = _response.order_by(Notes.created_date.desc()).paginate(pagination_parameters.page, pagination_parameters.page_size)
    pagination_parameters.item_count = _response.total
    return ResponseObject(data=_response.items,
                          page=PaginationObject(page=_response.page, total_pages=_response.pages,
                                                total=_response.total),
                          status=HTTPStatus.OK)


def fetch_note(note_id):
    try:
        _response = Notes.query.filter(Notes.id == note_id).one()
    except NoResultFound as e:
        abort(HTTPStatus.NOT_FOUND, message="Note not found.", exc=e)
    return ResponseObject(data=_response, status=HTTPStatus.OK)


def update_note(args, note_id, username):
    try:
        note = Notes.query.filter(Notes.id == note_id).one()
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
        note = Notes.query.filter(Notes.id == note_id).one()
    except NoResultFound as e:
        abort(HTTPStatus.NOT_FOUND, message="Note not found.", exc=e)

    try:
        db.session.delete(note)
        db.session.commit()
    except Exception as e:
        abort(HTTPStatus.BAD_GATEWAY, message="Note couldn't deleted.", exc=e)

    return ResponseObject(message="Note successfully deleted.", status=HTTPStatus.OK)


def get_pdf_key(note_id):
    try:
        note = Notes.query.filter(Notes.id == note_id).one()
    except NoResultFound as e:
        abort(HTTPStatus.NOT_FOUND, message="Note not found.", exc=e)
    pass

    if not note.has_attachment:
        abort(HTTPStatus.NOT_FOUND, message="Note has no attachment.", exc=e)

    file_service_download_url = current_app.config.get('FILE_SERVICE_DOWNLOAD_URL')
    pdf_service_key_url = current_app.config.get('PDF_SERVICE_KEY_URL')
    r = requests.post(
        pdf_service_key_url,
        json={'url': f'{file_service_download_url}/{note.attachment_file_key}?contentDisposition=inline'}
    )

    if r.status_code == 200 or r.status_code == 201:
        return ResponseObject(data={"pdfKey": r.text}, status=HTTPStatus.OK)
    else:
        return ResponseObject(message="Pdf key couldn't generated.", exc=e)
