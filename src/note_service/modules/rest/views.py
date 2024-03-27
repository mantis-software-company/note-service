from http import HTTPStatus

from flask.views import MethodView
from flask_smorest import Blueprint

from note_service.modules.rest.business import search_notes, create_note, fetch_note, update_note, delete_note, \
    get_file_url, search_item_count, upload_attachment_file, delete_attachment
from note_service.modules.rest.decorators import token_required
from note_service.modules.rest.schemas import Note, NoteFile, NotesResponse, NoteResponse, BaseResponse, NoteSearch, \
    AttachmentResponse

notes = Blueprint("Notes", "pets", url_prefix="/api/v1/notes", description="Not işlemleri için kullanılan servis")
attachments = Blueprint("Attachments", "pets", url_prefix="/api/v1/attachments",
                        description="Not ekleri işlemleri için kullanılan servis")


@notes.route("/")
class NotesCollection(MethodView):
    @token_required
    @notes.arguments(Note, location="json")
    @notes.response(HTTPStatus.CREATED, BaseResponse)
    @notes.alt_response(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, success=False, schema=BaseResponse)
    @notes.alt_response(status_code=HTTPStatus.BAD_GATEWAY, success=False, schema=BaseResponse)
    def post(self, args, username):
        """Yeni not oluşturmak için kullanılır"""
        return create_note(args, username)


@notes.route("/search")
class NoteSearchCollection(MethodView):
    @token_required
    @notes.arguments(NoteSearch, location="query")
    @notes.response(HTTPStatus.OK, NotesResponse)
    @notes.paginate()
    def get(self, args, pagination_parameters, **kwargs):
        """Verilen tag bilgisine göre not aramak için kullanılır"""
        return search_notes(args, pagination_parameters)


@notes.route("/search/count")
class NoteSearchCountCollection(MethodView):
    @token_required
    @notes.arguments(NoteSearch, location="query")
    @notes.response(HTTPStatus.OK, BaseResponse)
    def get(self, args, **kwargs):
        """Verilen tag bilgisine göre not aramak için kullanılır"""
        return search_item_count(args)


@notes.route("/<uuid:note_id>")
class NoteItemCollection(MethodView):
    @token_required
    @notes.response(HTTPStatus.OK, NoteResponse)
    @notes.alt_response(status_code=HTTPStatus.NOT_FOUND, success=False, schema=BaseResponse)
    def get(self, note_id, **kwargs):
        """ID bilgisi verilen notun detaylarını görüntülemek için kullanılır"""
        return fetch_note(note_id)

    @token_required
    @notes.arguments(Note, location="json")
    @notes.response(HTTPStatus.OK, BaseResponse)
    @notes.alt_response(status_code=HTTPStatus.NOT_FOUND, success=False, schema=BaseResponse)
    @notes.alt_response(status_code=HTTPStatus.BAD_GATEWAY, success=False, schema=BaseResponse)
    def put(self, args, note_id, **kwargs):
        """ID bilgisi verilen notu verilen parametrelere göre düzenlemek için kullanılır"""
        return update_note(args, note_id, **kwargs)

    @token_required
    @notes.response(HTTPStatus.OK, BaseResponse)
    @notes.alt_response(status_code=HTTPStatus.NOT_FOUND, success=False, schema=BaseResponse)
    @notes.alt_response(status_code=HTTPStatus.BAD_GATEWAY, success=False, schema=BaseResponse)
    def delete(self, note_id, **kwargs):
        """ID bilgisi verilen notu silmek için kullanılır"""
        return delete_note(note_id)


@notes.route("/<uuid:note_id>/attachmentUrls")
class NoteItemCollection(MethodView):
    @token_required
    @notes.response(HTTPStatus.OK, BaseResponse)
    @notes.alt_response(status_code=HTTPStatus.NOT_FOUND, success=False, schema=BaseResponse)
    def get(self, note_id, **kwargs):
        """Not'un ekini görüntülenmek için dosya urli oluşturur """
        return get_file_url(note_id)


@notes.route("/<uuid:note_id>/attachment/<uuid:attachment_file_key>")
class NoteAttachmentDeleteCollection(MethodView):
    @token_required
    @notes.response(HTTPStatus.OK, BaseResponse)
    @notes.alt_response(status_code=HTTPStatus.NOT_FOUND, success=False, schema=BaseResponse)
    @notes.alt_response(status_code=HTTPStatus.BAD_GATEWAY, success=False, schema=BaseResponse)
    def delete(self, note_id, attachment_file_key, **kwargs):
        """ID bilgisi verilen nottan file keyi verilen eki siler"""
        return delete_attachment(note_id, attachment_file_key)


@attachments.route("/upload")
class AttachmentUploadCollection(MethodView):
    @token_required
    @attachments.arguments(NoteFile, location="files")
    @attachments.response(HTTPStatus.CREATED, AttachmentResponse)
    @attachments.alt_response(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, success=False, schema=BaseResponse)
    @attachments.alt_response(status_code=HTTPStatus.BAD_GATEWAY, success=False, schema=BaseResponse)
    def post(self, files, **kwargs):
        """Ek yükler"""
        return upload_attachment_file(files)
