# deps for routing and upload
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
import time
import sys

#  deps for processing media
import imageio
import imageio.plugins.ffmpeg
import tqdm
from typing import Dict
import colorama
import imghdr
from colorama import Fore, Style

from .utils.centerface import CenterFace
from .utils.handle_frames import draw_replacements, process_frame, image_detect

from pathlib import Path
from dotenv import load_dotenv

app = Flask(__name__)
UPLOAD_FOLDER = "/home/ibex/Github/face-replace/server/app/static"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# with open(".config.json") as f:
#    config = json.load(f)
configVal = '{"SECRET_KEY": "vZ3HJbDJW2CgzA!"}'
config = json.loads(configVal)
app.config.update(config)
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
# set the client's upload folder to the flask static dir
app.config["DEBUG"] = True
# app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
# Expose cors headers to enable file download
CORS(app, expose_headers="Authorization")


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")


@app.route("/upload", methods=["GET", "POST"])
def fileUpload():
    if request.method == "POST":
        if "file" not in request.files:
            print("No file uploaded")
            return redirect(request.url)

    f_path = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"])
    if not os.path.isdir(f_path):
        os.mkdir(f_path)

    file = request.files["file"]
    file_replacement = request.form.get("replacement")
    file_scale = request.form.get("scale")
    filename = secure_filename(file.filename)
    file_ext = filename.split(".")[0]
    if file_ext != validate_image(file.stream):
        print("Failure: Image extension filetype not recognized")

    destination = "/".join([f_path, filename])
    file.save(destination)
    file_length = os.stat(destination).st_size
    session["uploadFilePath"] = destination
    mime = mimetypes.guess_type(destination)[0]

    print("mime is ", mime)
    if mime is None:
        return None

    processed_file_title = filename.split(".")[0]
    processed_file_ext = filename.split(".")[1]
    processed_file_name = (
        f"{processed_file_title}_{file_replacement}.{processed_file_ext}"
    )

    session["processedFileName"] = processed_file_name

    emoji = {
        "base_path": f"{f_path}/emojis/",
        "path": "",
        "type": "",
        "selected": "",
        "resolved": False,
    }

    if mime.startswith("video"):
        if file_replacement == "emoji":
            emoji["type"] = "video"
        face_replace(
            destination, file_replacement, "video", emoji, file_scale,
        )
        return send_from_directory(f_path, processed_file_name, as_attachment=True)

    elif mime.startswith("image"):
        if file_replacement == "emoji":
            emoji["type"] = "image"
        face_replace(
            destination, file_replacement, "image", emoji, file_scale,
        )
        return send_from_directory(f_path, processed_file_name, as_attachment=True)

    else:
        print("unknown mimetype")
        return ""


# uncomment for debug
# @app.route("/", defaults={"u_path": ""})
# @app.route("/<path:u_path>")
# def catch_all(u_path):
#    print("in catch_all, args are: ", sys.argv)
#    print(repr(u_path))
#    return ""


@app.route("/")
def renderHome():
    return redirect(request.url)


def video_detect(
    ipath: str,
    opath: str,
    centerface: str,
    threshold: float,
    nested: bool,
    replacewith: str,
    emoji: str,
    mask_scale: float,
    ellipse: bool,
    ffmpeg_config: Dict[str, str],
):
    try:
        reader: imageio.plugins.ffmpeg.FfmpegFormat.Reader = imageio.get_reader(ipath)
        meta = reader.get_meta_data()
        _ = meta["size"]
    except:
        print(
            Fore.RED
            + f"Could not open file {ipath} as a video file with imageio. Make sure ffmpeg is installed on system, and try converting video to MP4 format"
        )
        return

    read_iter = reader.iter_data()
    nframes = reader.count_frames()
    print("initializing frame sessions")
    session["frames"] = nframes
    print(Fore.GREEN + "Step 3: Process Frames and Draw Replacements")
    if nested:
        bar = tqdm.tqdm(dynamic_ncols=True, total=nframes, position=1, leave=True)
    else:
        bar = tqdm.tqdm(dynamic_ncols=True, total=nframes)

    if opath is not None:
        writer: imageio.plugins.ffmpeg.FfmpegFormat.Writer = imageio.get_writer(
            opath, format="FFMPEG", mode="I", fps=meta["fps"], **ffmpeg_config
        )
    for frame in enumerate(read_iter):
        frame_index, current_frame = frame
        # Perform network inference, get bb dets but discard landmark predictions
        dets, _ = centerface(current_frame, threshold=threshold)

        process_frame(
            dets,
            current_frame,
            mask_scale=mask_scale,
            replacewith=replacewith,
            emoji=emoji,
            ellipse=ellipse,
        )

        if opath is not None:
            writer.append_data(current_frame)
        bar.update()
    reader.close()
    if opath is not None:
        writer.close()
    bar.close()


def face_replace(file, file_replacement, filetype, emoji, file_scale):
    print(Fore.GREEN + "Step 1 Processing file... ", file)
    ipaths = [file]
    base_opath = None
    replacewith = file_replacement
    emoji = emoji
    threshold = 0.2
    ellipse = True
    mask_scale = 1.3
    ffmpeg_config = {}
    backend = "auto"
    in_shape = None

    print("scaling to ", file_scale)
    if not file_scale == "default":
        w, h = file_scale.split("x")
        in_shape = int(w), int(h)
    elif file_scale == "default":
        print("self.in_shape is none")
        if filetype == "image":
            img_dims = imageio.imread(ipaths[0])
            w, h = img_dims.shape[:2]
            in_shape = int(w), int(h)

    # TODO: scalar downscaling setting (-> in_shape), preserving aspect ratio
    # Downscale images for network inference to this size
    centerface = CenterFace(in_shape=in_shape, backend=backend)

    multi_file = len(ipaths) > 1
    if multi_file:
        ipaths = tqdm.tqdm(
            ipaths, position=0, dynamic_ncols=True, desc="Batch progress"
        )

    for ipath in ipaths:
        opath = base_opath
        if opath is None:
            root, ext = os.path.splitext(ipath)
            opath = f"{root}_{file_replacement}{ext}"
        print(Fore.BLUE + f"Input:  {ipath}\nOutput: {opath}")
        if opath is None:
            print(Fore.RED + "No output file is specified, no output will be produced.")
        if filetype == "video":
            print(Fore.GREEN + "Step 2: Video Detect")
            video_detect(
                ipath=ipath,
                opath=opath,
                centerface=centerface,
                threshold=threshold,
                replacewith=replacewith,
                emoji=emoji,
                mask_scale=mask_scale,
                ellipse=ellipse,
                nested=multi_file,
                ffmpeg_config=ffmpeg_config,
            )
        elif filetype == "image":
            print(Fore.GREEN + "Step 2: Image Detect")
            print(Fore.GREEN + "Step 3: Process Frames and Draw Replacements")
            image_detect(
                ipath=ipath,
                opath=opath,
                centerface=centerface,
                threshold=threshold,
                replacewith=replacewith,
                emoji=emoji,
                mask_scale=mask_scale,
                ellipse=ellipse,
            )
        else:
            print(
                Fore.RED + f"File {ipath} has an unknown type {filetype}. Skipping..."
            )


if __name__ == "__main__":
    main()
