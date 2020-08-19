import os
from typing import Dict, Tuple
from flask import session
import tqdm
import skimage.draw
import numpy as np
import imageio
import imageio.plugins.ffmpeg
import cv2
import colorama
from colorama import Fore, Style
from .centerface import CenterFace
from .emoji import get_emoji_size_path, select_random_emoji

# TODO: Optionally preserve audio track?

# refactor scaling (mask scale isnt used here)
def scale_bb(x1, y1, x2, y2, mask_scale=1.0):
    s = mask_scale - 1.0
    h, w = y2 - y1, x2 - x1
    y1 -= h * s
    y2 += h * s
    x1 -= w * s
    x2 += w * s
    return np.round([x1, y1, x2, y2]).astype(int)


def draw_det(
    frame,
    score,
    det_idx,
    x1,
    y1,
    x2,
    y2,
    replacewith,
    emoji,
    ellipse: bool = True,
    ovcolor: Tuple[int] = (0, 0, 0),
):
    if replacewith == "solid":
        cv2.rectangle(frame, (x1, y1), (x2, y2), ovcolor, -1)
    elif replacewith == "emoji":

        # get dims of face to be replaced
        face_height, face_width = frame[y1:y2, x1:x2].shape[:2]

        # check face dims to decide on emoji size (minimizes resizing necessary)
        emoji_path_extension = get_emoji_size_path(face_height, face_width)

        if emoji_path_extension:
            emoji["path"] = emoji["base_path"] + emoji_path_extension
        else:
            emoji["path"] = emoji["base_path"]

        # when replacing faces in an img use a different, random emoji for each face
        if emoji["type"] == "image":
            emoji["selected"] = select_random_emoji()

        # when replacing video faces: use a single emoji for all faces in all frames (avoid slowing down video processing)
        elif emoji["type"] == "video":
            if not emoji["resolved"]:
                emoji["resolved"] = True
                emoji["selected"] = select_random_emoji()

        # combine emoji and path, read image with cv2
        emoji_location = emoji["path"] + emoji["selected"]
        emoji_img = cv2.imread(emoji_location)
        emoji_height, emoji_width, = emoji_img.shape[:2]

        # use the greater dim from face to determine emoji height / width
        if face_width > face_height:
            emoji_scale = face_width
        else:
            emoji_scale = face_height

        try:
            scaled_img = cv2.resize(emoji_img, (emoji_scale, emoji_scale))
        except cv2.error as e:
            print(Fore.RED + "Invalid frame!")

        # wait until the resize has completed before moving on
        cv2.waitKey()

        roibox = frame[y1:y2, x1:x2]
        # Get y and x coordinate lists of the "bounding ellipse"
        ey, ex = skimage.draw.ellipse(
            (y2 - y1) // 2, (x2 - x1) // 2, (y2 - y1) // 2, (x2 - x1) // 2
        )

        roibox[ey, ex] = scaled_img[ey, ex]

        frame[y1:y2, x1:x2] = roibox

    elif replacewith == "blur":
        bf = 2  # blur factor (number of pixels in each dimension that the face will be reduced to)

        blurred_box = cv2.blur(
            frame[y1:y2, x1:x2], (abs(x2 - x1) // bf, abs(y2 - y1) // bf)
        )
        if ellipse:
            roibox = frame[y1:y2, x1:x2]
            # Get y and x coordinate lists of the "bounding ellipse"
            ey, ex = skimage.draw.ellipse(
                (y2 - y1) // 2, (x2 - x1) // 2, (y2 - y1) // 2, (x2 - x1) // 2
            )
            roibox[ey, ex] = blurred_box[ey, ex]
            frame[y1:y2, x1:x2] = roibox
        else:
            frame[y1:y2, x1:x2] = blurred_box
    elif replacewith == "none":
        pass


def process_frame(dets, frame, mask_scale, replacewith, emoji, ellipse):
    # TODO: store dets and i in session, get progress frontend
    for i, det in enumerate(dets):
        boxes, score = det[:4], det[4]
        x1, y1, x2, y2 = boxes.astype(int)
        x1, y1, x2, y2 = scale_bb(x1, y1, x2, y2, mask_scale)
        # TODO: pass emoji here?
        # Clip bb coordinates to valid frame region
        y1, y2 = max(0, y1), min(frame.shape[0] - 1, y2)
        x1, x2 = max(0, x1), min(frame.shape[1] - 1, x2)

        draw_det(
            frame,
            score,
            i,
            x1,
            y1,
            x2,
            y2,
            replacewith=replacewith,
            emoji=emoji,
            ellipse=ellipse,
        )


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
    print("read iter is ", read_iter)
    nframes = reader.count_frames()
    print(Fore.GREEN + "Step 3: Process Frames and Draw Replacements")
    if nested:
        bar = tqdm.tqdm(dynamic_ncols=True, total=nframes, position=1, leave=True)
    else:
        bar = tqdm.tqdm(dynamic_ncols=True, total=nframes)

    if opath is not None:
        writer: imageio.plugins.ffmpeg.FfmpegFormat.Writer = imageio.get_writer(
            opath, format="FFMPEG", mode="I", fps=meta["fps"], **ffmpeg_config
        )
    # TODO store session value here for read iter
    for frame in read_iter:
        # TODO store session value here for frame
        # Perform network inference, get bb dets but discard landmark predictions
        dets, _ = centerface(frame, threshold=threshold)
        # TODO loop over dets here, select emoji
        process_frame(
            dets,
            frame,
            mask_scale=mask_scale,
            replacewith=replacewith,
            emoji=emoji,
            ellipse=ellipse,
        )

        if opath is not None:
            writer.append_data(frame)
        bar.update()
    reader.close()
    if opath is not None:
        writer.close()
    bar.close()


def image_detect(
    ipath: str,
    opath: str,
    centerface: str,
    threshold: float,
    replacewith: str,
    emoji: str,
    mask_scale: float,
    ellipse: bool,
):
    frame = imageio.imread(ipath)
    # Perform network inference, get bb dets but discard landmark predictions
    dets, _ = centerface(frame, threshold=threshold)
    # TODO loop over dets here, select emoji
    process_frame(
        dets,
        frame,
        mask_scale=mask_scale,
        replacewith=replacewith,
        emoji=emoji,
        ellipse=ellipse,
    )
    imageio.imsave(opath, frame)


def face_replace(file, file_options, filetype, emoji):
    print(Fore.GREEN + "Step 1 Processing file... ", file)
    ipaths = [file]
    base_opath = None
    replacewith = file_options
    emoji = emoji
    threshold = 0.2
    ellipse = True
    mask_scale = 1.3
    # TODO: debug auto codec
    # ffmpeg_config = {"codec": "libx264"}
    ffmpeg_config = {}
    # TODO pass backend from .env file or front end
    # backend = "auto"
    backend = "auto"
    in_shape = None
    if in_shape is not None:
        w, h = in_shape.split("x")
        in_shape = int(w), int(h)
        # TODO: this is never used

    # TODO: scalar downscaling setting (-> in_shape), preserving aspect ratio
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
            opath = f"{root}_{file_options}{ext}"
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
