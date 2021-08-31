# [https://face-replace.net](https://face-replace.net) Live site now available

# Description
Simple react/ flask webapp that can be run fully locally for replacing all faces in images and video

# Overview

React Flask GUI app to replace faces frame by frame in Video or Images with Emojis, Boxes or Blur. Uses react for front end file uploading, api calls, and rendering processed media after making replacements. Centerface & Deface are used for facial recognition and ImageIO for image processing. Originally adapted from the <a href="https://www.github.com/ORB-HD/deface">deface</a> module from CLI format to a simple flask web app.

Demo of video with emoji replacements (Home Alone 2 trailer)
![FaceReplace Demo1b](/demos/official-demo-2-emoji-optimized.gif) 

Demo of video with a Random emoji used in each frame as replacements (Home Alone 2 trailer)
![FaceReplace Demo1](/demos/homealone2_1min-2_30min_emoji.gif)

Screen shot of the React front end (for uploading images or video)
<img src="demos/face-replace-frontend.png" />
Demo of video with a single emoji used in each frame for replacements. (Scene from Independence Day)

![FaceReplace Demo2](/demos/IndependenceDayRooftop_emoji.gif)

Demo of image, large crowd with emoji replacements 
<img src="demos/crowd_emoji.jpeg" align="center" />
<img src="demos/crowd2_emoji.jpeg" align="center" />

Demo of image, large crowd with blur effect
<img src="demos/crowd_blurred.jpeg" align="center" />

Demo of image, large crowd with boxes effect
<img src="demos/crowd_boxes.jpeg" align="center" />

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

  Install the Client:

  '''
  cd face-replace/server/app/client && npm upgrade && npm install
  '''

  Run the Client:

  '''
  npm start
  '''

  Edit the file config.json in the server/ directory, and update the SECRET_KEY used for flask debugging. 

  {
      "SECRET_KEY": "exampleKey"
  }

  Install and run the Flask Backend:

  '''
  cd server
  python3 -m venv venv
  pip3 install --upgrade pip
  source venv/bin/activate
  pip3 install -r requirements.txt
  '''

  Note: if installation of onnx hangs in pip try:

  ```
  sudo apt-get install protobuf-compiler libprotoc-dev pip install onnx
  ```


  Run Flask:

  '''
  cd server
  flask run
  '''

  Note: the .env file in /server/ should take care of setting all of the 
  required  variables for flask, while SECRET_KEY should be set in 
  config.json in the root directory

  If installation of opencv-python (in requirements.txt) hangs you can use ctrl c to stop the installation. The app should still work (tested on debian buster) as long as all the preceding packages are installed. Alternatively try installing the following dependencies with apt (or brew):
   
  '''
  sudo apt install python-opencv python3-imageio python3-numpy -y
  '''

  Also install ffmpeg (required) on your system with:

  '''
  sudo apt install ffmpeg
  '''

  If you have issues with the flask/react proxy make sure this line is in your
  package.json:

  "proxy" : "http://localhost:5000",
  and setupProxy includes the correct url / port


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

Run the Flask API locally:
```
cd face-replace
cd server
flask run
```

Run the React Client locally:
```
cd face-replace
cd client
npm start
```


  1. Open a browser and go to https://localhost:3000
  2. Upload a image or video file
  3. Download the file

# Note:
The accuracy of the output media will depend on resolution and settings, results can be improved by tweaking options in the deface module and app:

server/app/app.py
And
server/app/utils/centerface.py

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
