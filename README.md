FaceReplace

![FaceReplace Demo](/demos/IndependenceDayEmoji640x360.gif)
![FaceReplace Demo2](/demos/emojiCrowd2.jpeg)

Video demos coming soon

# Overview

  React Flask GUI app to replace faces in Video or Images with Emojis, Boxes or Blur. Uses Centerface & Deface for facial recognition and ImageIO for image processing. Originally adapted from the <a href="link">deface</a> module from CLI format to a simple flask web app.

# Installation

  Install/ upgrade the latest version of node/npm:
  Instructions https://github.com/nodesource/distributions/blob/master/README.md

  Install/ Upgrade to latest version of npm:
  ```
  sudo apt install npm -y
  sudo npm cache clean -f
  sudo npm install -g n
  upgrade npm
  sudo npm install npm@latest -g
   ```

  Requirements:
    1. Required for videos only (you may be able to use python-ffmpeg or the imageio-ffmpeg extension
    2. python-opencv 


  Install and run the Client:

  '''
  cd face-replace/server/app/client && npm upgrade && npm install
  '''

  Run the Client:

  '''
  npm start
  '''

  Create a file config.json in the root directory, and set a SECRET_KEY

  {
      "SECRET_KEY": "exampleKey"
  }

  Install and run the Flask Backend:

  '''
  cd server
  python3 -m venv venv
  source venv/bin/activate
  pip3 install -r requirements.txt
  '''

  (Optional) upgrade requirements:

  '''
  pip3 install pur
  pur -r requirements.txt
  '''

  Run Flask:

  '''
  cd server
  flask run
  '''

  Note: the .env file in /server/ should take care of setting all of the 
  required  variables for flask, while SECRET_KEY should be set in 
  config.json in the root directory

  If installation of opencv-python hangs make sure you have a 
  compiler installed and try:
   
  '''
  sudo apt install python-opencv
  '''

  If you have any issues processing video files, install ffmpeg with:

  '''
  sudo apt install ffmpeg
  '''

  If you have issues with the flask/react proxy make sure this line is in your
  package.json:

  "proxy" : "http://localhost:5000",
  and setupProxy includes the correct path


--------------------------------------------------------------------------------

# Note

  1. If you do not have a GPU available, video processing can take awhile but 
     the pip3 package onnxruntime will help

  2. This app uses code from https://github.com/ORB-HD/deface which is a CLI tool. Because of this some options passed to face_replace (based on deface) use default values.
  
  Depending on your system these can be tweaked (some can be changed in the front end upload form)

--------------------------------------------------------------------------------

# Features

  ## Backend:

    Features:
        Fully offline
        Image and video replacement/ anonymization with emojis, boxes, or blur

      Stack:
        Flask

      Depends on:
        Deface pip3 module

      Local Proxy:
        flask session and flask_cors to process requests from frontend

  ## Frontend:

    Features:
      Form for uploading files
      Material UI

    Stack:
      React.js

    Local Proxy:
      setupProxy.js
      package.json "proxy" port 5000
      http-proxy-middleware

--------------------------------------------------------------------------------

# Usage:

  1. Open a browser and go to https://localhost:3000
  2. Upload a image or video file
  3. Download the file

--------------------------------------------------------------------------------

# Credit:

  https://github.com/ORB-HD/deface
  ONNX
  Centerface
  cv2
  ImageIO


--------------------------------------------------------------------------------

# Additional relevant docs taken from the original deface CLI module (for more see https://github.com/ORB-HD/deface)


### Drawing black boxes

By default, each detected face is anonymized by applying a blur filter to an ellipse region that covers the face. If you prefer to anonymize faces by drawing black boxes on top of them, you can achieve this through the `--boxes` and `--replacewith` options:

    $ deface examples/city.jpg --boxes --replacewith solid -o examples/city_anonymized_boxes.jpg

<img src="examples/city_anonymized_boxes.jpg" width="70%" alt="$ deface examples/city.jpg --enable-boxes --replacewith solid -o examples/city_anonymized_boxes.jpg"/>


### Tuning detection thresholds

The detection threshold (`--thresh`, `-t`) is used to define how confident the detector needs to be for classifying some region as a face. By default this is set to the value 0.2, which was found to work well on many test videos.

If you are experiencing too many false positives (i.e. anonymization filters applied at non-face regions) on your own video data, consider increasing the threshold.
On the other hand, if there are too many false negative errors (visible faces that are not anonymized), lowering the threshold is advisable.

The optimal value can depend on many factors such as video quality, lighting conditions and prevalence of partial occlusions. To optimize this value, you can set threshold to a very low value and then draw detection score overlays, as described in the [section below](#drawing-detection-score-overlays).

To demonstrate the effects of a threshold that is set too low or too high, see the examples outputs below:

`--thresh 0.02` (notice the false positives, e.g. at hand regions) | `--thresh 0.7` (notice the false negatives, especially at partially occluded faces)
:--:|:--:
![examples/city_anonymized_thresh0.02.jpg](examples/city_anonymized_thresh0.02.jpg) | ![$ deface examples/city_anonymized_thresh0.7.jpg](examples/city_anonymized_thresh0.7.jpg)


### High-resolution media and performance issues 

Since `deface` tries to detect faces in the unscaled full-res version of input files by default, this can lead to performance issues on high-res inputs (>> 720p). In extreme cases, even detection accuracy can suffer because the detector neural network has not been trained on ultra-high-res images.

To counter these performance issues, `deface` supports downsampling its inputs on-the-fly before detecting faces, and subsequently rescaling detection results to the original resolution. Downsampling only applies to the detection process, whereas the final output resolution remains the same as the input resolution.

This feature is controlled through the `--scale` option, which expects a value of the form `WxH`, where `W` and `H` are the desired width and height of downscaled input representations.
It is very important to make sure the aspect ratio of the inputs remains intact when using this option, because otherwise, distorted images are fed into the detector, resulting in decreased accuracy.

For example, if your inputs have the common aspect ratio 16:9, you can instruct the detector to run in 360p resolution by specifying `--scale 640x360`.
If the results at this fairly low resolution are not good enough, detection at 720p input resolution (`--scale 1280x720`) may work better.


## Hardware acceleration

Depending on your available hardware, you can often speed up neural network inference by enabling the optional [ONNX Runtime](https://microsoft.github.io/onnxruntime/) backend of `deface`.

### CUDA (on Nvidia GPUs)

If you have a CUDA-capable GPU, you can enable GPU acceleration by installing the relevant packages:

    $ python3 -m pip install onnx onnxruntime-gpu

If the `onnxruntime-gpu` package is found and a GPU is available, the face detection network is automatically offloaded to the GPU.
This can significantly improve the overall processing speed.

### Other platforms

If your machine doesn't have a CUDA-capable GPU but you want to accelerate computation on another hardware platform (e.g. Intel CPUs), you can look into the available options in the [ONNX Runtime build matrix](https://microsoft.github.io/onnxruntime/).


## How it works

The included face detection system is based on CenterFace ([code](https://github.com/Star-Clouds/centerface), [paper](https://arxiv.org/abs/1911.03599)), a deep neural network optimized for fast but reliable detection of human faces in photos.
The network was trained on the [WIDER FACE](http://shuoyang1213.me/WIDERFACE/) dataset, which contains annotated photos showing faces in a wide variety of scales, poses and occlusions.

Although the face detector is originally intended to be used for normal 2D images, `deface` can also use it to detect faces in video data by analyzing each video frame independently.
The face bounding boxes predicted by the CenterFace detector are then used as masks to determine where to apply anonymization filters.


## Credits

- `centerface.onnx` (original) and `centerface.py` (modified) are based on https://github.com/Star-Clouds/centerface (revision [8c39a49](https://github.com/Star-Clouds/CenterFace/tree/8c39a497afb78fb2c064eb84bf010c273bb7d3ce)),
  [released under MIT license](https://github.com/Star-Clouds/CenterFace/blob/36afed/LICENSE).
- The original source of the example images in the `examples` directory can be found [here](https://www.pexels.com/de-de/foto/stadt-kreuzung-strasse-menschen-109919/) (released under the [Pexels photo license](https://www.pexels.com/photo-license/)).
