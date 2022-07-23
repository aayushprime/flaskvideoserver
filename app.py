from flask import (
    Flask,
    Response,
    request,
    jsonify,
    stream_with_context,
    make_response,
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

from flask_expects_json import expects_json
from jsonschema import ValidationError
from helpers import (
    calculate_price,
    allowed_filetype,
    get_uploading_files,
    UploadingFileEntry,
)
from video_validator import validate_video
from schemas import metadata_schema
from stream import read_file_chunks
from provider import LocalStorageProvider

import os, uuid, json, sqlite3

app = Flask(__name__)
db = sqlite3.connect("db.sqlite3", check_same_thread=False)
localStorage = LocalStorageProvider(db)


@app.route("/video/<video_id>", methods=["GET"])
def get_video(video_id):
    """
    Route to get a video previously stored on the server
    """

    item = localStorage.get_item(video_id)
    if item is None:
        return jsonify({"error": "video not found"})
    else:
        return Response(
            stream_with_context(read_file_chunks(item)),
            mimetype="video/mp4",
            direct_passthrough=True,
        )


@app.route("/videos", methods=["POST", "GET"])  # POST
def upload_video():

    if request.method == "POST":
        """
        Accept video file in a form data with the key "video".
        """
        # preliminary size check
        if request.content_length > 1e9:
            return jsonify({"error": "Only videos <1GB are supported"})

        with UploadingFileEntry(request.content_length, db, uuid.uuid4()) as entry:
            # get the file from request (uploading)
            f = request.files.get("video")
            if f is None:
                return jsonify(
                    {"success": False, "error": "'video' key must exist for POST"}
                )

            # preliminary file type check
            if not allowed_filetype(f.filename):
                return jsonify(
                    {
                        "success": False,
                        "error": "Invalid file name or unsupported file type. Only mkv and mp4 are supported.",
                    }
                )

            id = os.path.join(str(uuid.uuid4()) + secure_filename(f.filename))
            # save file to disk
            save_path = localStorage.set_item(id, f)
            f.stream.close()

        isInvalid, error, data = validate_video(save_path)
        if isInvalid:
            # delete the invalid file
            localStorage.remove(save_path)
            return jsonify({"success": False, "error": error})
        else:
            # TODO: connect to the auth server and charge the user
            # price = calculate_price(data[0], data[1])
            return jsonify({"success": True, "id": id})

    elif request.method == "GET":
        """
        Return a list of all videos.
        """
        query = request.args.get("query")
        after = request.args.get("timestamp")
        videos = localStorage.search(query, after)
        return jsonify({"videos": videos})
    else:
        return jsonify({"error": "method not supported"})


@app.route("/currently_uploading", methods=["GET"])
def list_videos():
    """
    Return a list of currently uploading files
    """
    return jsonify(get_uploading_files(db))


@app.route("/prices", methods=["POST"])
@expects_json(metadata_schema)
def get_prices():
    """
    Receive size (in MB) and length (in seconds) of the video.
    Return the price of the video.
    """
    video_size = request.json.get("size")
    video_length = request.json.get("length")

    price = calculate_price(size=video_size, length=video_length)
    return jsonify({"price": price})


@app.errorhandler(HTTPException)
def handle_exception(e):
    """
    Return JSON instead of HTML for HTTP errors.
    (To behave as a JSON API).
    """
    response = e.get_response()
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


@app.errorhandler(400)
def bad_request(error):
    """
    defining error handler for status 400 validation errors
    """
    if isinstance(error.description, ValidationError):
        original_error = error.description
        return make_response(jsonify({"error": original_error.message}), 400)
    # handle other "Bad Request"-errors
    return error


app.run()
