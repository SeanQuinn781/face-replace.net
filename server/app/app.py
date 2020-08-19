import os
import asyncio
from flask import Flask, request, redirect, session, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import argparse
import glob
import json
import mimetypes
import random
import os
import sys
from .face_replace import face_replace

# TODO validation
# from .allowedFile import allowedFileExtension, allowedFileType
from pathlib import Path
from dotenv import load_dotenv

app = Flask(__name__)
UPLOAD_FOLDER = "static"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
with open("./config.json") as f:
    config = json.load(f)
app.config.update(config)
# app.debug = True
# used to set env to development since that is preferred over setting it in config file
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
# set the client's upload folder to the static dir, making contents accessible
# on the client side
app.config["DEBUG"] = True
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
# Expose cors headers to enable file download
CORS(app, expose_headers="Authorization")


@app.route("/upload", methods=["GET", "POST"])
def fileUpload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")

    f_path = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"])
    if not os.path.isdir(f_path):
        os.mkdir(f_path)

    file = request.files["file"]
    file_options = request.form.get("fileOptions")
    filename = secure_filename(file.filename)
    mime_type = file.content_type

    # validFileType = allowedFileType(mime_type)
    # if not allowedFileExtension(file.filename) or validFileType == False:
    destination = "/".join([f_path, filename])
    # need this? save in memory or session instead?
    file.save(destination)
    file_length = os.stat(destination).st_size
    session["uploadFilePath"] = destination
    mime = mimetypes.guess_type(destination)[0]
    if mime is None:
        return None

    processed_file_title = filename.split(".")[0]
    processed_file_ext = filename.split(".")[1]
    processed_file_name = f"{processed_file_title}_{file_options}.{processed_file_ext}"

    session["processedFileName"] = processed_file_name

    emoji = {
        "base_path": f"{f_path}/emojis/",
        "path": "",
        "type": "",
        "selected": "",
        "resolved": False,
    }

    session["frames"] = 0
    session["currentFrame"] = 0

    if mime.startswith("video"):
        if file_options == "emoji":
            emoji["type"] = "video"
        face_replace(
            destination, file_options, "video", emoji,
        )
        return send_from_directory(f_path, processed_file_name, as_attachment=True)

    elif mime.startswith("image"):
        if file_options == "emoji":
            emoji["type"] = "image"
        face_replace(
            destination, file_options, "image", emoji,
        )
        return send_from_directory(f_path, processed_file_name, as_attachment=True)

    else:
        print("unknown mimetype")
        return ""


@app.route("/download/<path:filename>", methods=["GET", "POST"])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config["UPLOAD_FOLDER"])
    return send_from_directory(directory=uploads, filename=filename)


@app.route("/", defaults={"u_path": ""})
@app.route("/<path:u_path>")
def catch_all(u_path):
    print("in catch_all, args are: ", sys.argv)
    print(repr(u_path))
    return "ok"
