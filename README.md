================================================================================
      _____                     ____                _                    
     |  ___|  __ _   ___   ___ |  _ \   ___  _ __  | |  __ _   ___   ___
     | |_   / _` | / __| / _ \ | |_) | / _ \| '_ \ | | / _` | / __| / _ \
     | _ | | (_| || (__ |  __/ |  _ < |  __/| |_) || || (_| || (__ |  __/
     |_|    \__,_| \___| \___| |_| \_\ \___|| .__/ |_| \__,_| \___| \___|
                                            |_|

================================================================================

# OVERVIEW

  A simple app adapting the <a href="link">deface</a> module from CLI format to
  a simple flask web app.

# INSTALLATION

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
  cd client && npm upgrade && npm install
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

# ISSUES

  1. If you do not have a GPU available, video processing can take awhile but 
     the pip3 package onnxruntime will help

  2. This app uses code from https://github.com/ORB-HD/deface which is a CLI tool.
     Because of this some options passed to face_replace (based on deface) use default values.
     Depending on your system these can be tweaked (some can be changed in the 
     front end upload form)

--------------------------------------------------------------------------------

# FEATURES

  ## Backend:

    Features:
        Fully offline
        Image and video anonymization

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

# USAGE:

  1. Open a browser and go to https://localhost:3000
  2. Upload a image or video file
  3. Download the file

--------------------------------------------------------------------------------

# INSPIRED BY:

  pypi.com/deface by ORB-HD
  ONNX
  Centerface
  cv2
  ImageIO