import os
from typing import Tuple
from flask import session
import skimage.draw
import numpy as np
import imageio
import cv2
import colorama
from colorama import Fore, Style
import utils
from utils.centerface import CenterFace
from utils.emoji import get_emoji_size, select_emoji


def scale_bb(x1, y1, x2, y2, mask_scale=1.0):
    s = mask_scale - 1.0
    h, w = y2 - y1, x2 - x1
    y1 -= h * s
    y2 += h * s
    x1 -= w * s
    x2 += w * s
    return np.round([x1, y1, x2, y2]).astype(int)


def draw_replacements(
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
        emoji_path_extension = get_emoji_size(face_height, face_width)

        print("emoji path extension", emoji_path_extension)


        if emoji_path_extension:
            emoji["path"] = emoji["base_path"] + emoji_path_extension
        else:
            emoji["path"] = emoji["base_path"]

        print("emoji path is ", emoji["path"])
    
        # when replacing faces in an img use a different, random emoji for each face
        if emoji["type"] == "image":
            emoji["selected"] = select_emoji()

        # when replacing video faces: use a single emoji for all faces in all frames (avoid slowing down video processing)
        elif emoji["type"] == "video":
            if not emoji["resolved"]:
                emoji["resolved"] = True
                emoji["selected"] = select_emoji()
            if not len(emoji["selected"]) > 2:
                print("no emoji selected, emoji is ", emoji)

        # combine emoji and path, read image with cv2
        emoji_location = emoji["path"] + emoji["selected"]
        print(emoji_location)
        emoji_img = cv2.imread(emoji_location)
        print('emoji img ', emoji_img)
        (emoji_height, emoji_width,) = emoji_img.shape[:2]

        # use the greater dim from face to determine emoji height / width
        if face_width > face_height:
            alt_dimension = face_height
            emoji_scale = face_width
            try:
                scaled_emoji = cv2.resize(emoji_img, (emoji_scale, alt_dimension))
            except cv2.error as e:
                print(Fore.RED + "Invalid frame!")
            # wait until the resize has completed before moving on
            cv2.waitKey()

        else:
            alt_dimension = face_width
            emoji_scale = face_height

            try:
                scaled_emoji = cv2.resize(emoji_img, (alt_dimension, emoji_scale))
            except cv2.error as e:
                print(Fore.RED + "Invalid frame!")
            # wait until the resize has completed before moving on
            cv2.waitKey()

        roibox = frame[y1:y2, x1:x2]
        # Get y and x coordinate lists of the "bounding ellipse"
        ey, ex = skimage.draw.ellipse(
            (y2 - y1) // 2, (x2 - x1) // 2, (y2 - y1) // 2, (x2 - x1) // 2
        )
        # Apply bounding box ellipse it to the emoji
        roibox[ey, ex] = scaled_emoji[ey, ex]

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
    for i, det in enumerate(dets):
        boxes, score = det[:4], det[4]
        x1, y1, x2, y2 = boxes.astype(int)
        x1, y1, x2, y2 = scale_bb(x1, y1, x2, y2, mask_scale)
        # Clip bb coordinates to valid frame region
        y1, y2 = max(0, y1), min(frame.shape[0] - 1, y2)
        x1, x2 = max(0, x1), min(frame.shape[1] - 1, x2)

        draw_replacements(
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
    process_frame(
        dets,
        frame,
        mask_scale=mask_scale,
        replacewith=replacewith,
        emoji=emoji,
        ellipse=ellipse,
    )
    imageio.imsave(opath, frame)


if __name__ == "__main__":
    main()
