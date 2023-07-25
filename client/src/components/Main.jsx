import React from 'react'
import { Button } from '@material-ui/core';
import Loader from 'react-loader-spinner';

class Main extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      mediaURL: "Pending Upload",
      fileUploaded: false,
      fileProcessing: false,
      videoUrl: false,
      fileType: "image",
      imageUrl: false,
      replacement: 'emoji',
      scale: 'default',
    };

  }

  handleError = (msg) => {
    alert(msg)
    return;
  }

  handleUpload = (e) => {

    e.preventDefault();
    const data = new FormData();

    // Make sure some files are actually being uploaded
    if (this.uploadInput.files.length === 0) {
      this.handleError('No files to upload, please upload an image or video file');
    }

    else if (this.uploadInput.files[0].name) {
      // Display loading animation until file has been sent to backend and finished processing
      this.setState({ fileProcessing: true })

      // Check mimetype, determine if upload media is an img or video
      // this package is no longer supported, and is why sometimes its better not to use tiny utils in npm :-)
      // NOTE removing this broken dependency: let mType = mime.lookup(this.uploadInput.files[0].name)
      let fileName = this.uploadInput.files[0].name;
      let fileExt = fileName.split(".")[1];
      console.log('now fileExt is: ', fileExt)
      let fileType;

      if (fileExt) {
	      console.log('ext is ', fileExt)
        // mType = mType.split('/')[0] === 'image' ? 'image' : 'video'
        if (fileExt.includes("png") || fileExt == "jpg" || fileExt == "jpeg") {
          fileType = 'image';
          this.setState({ fileType: "image" })
        }
      } else {
        fileType = 'video';
        this.setState({ fileType: "video" })
        // uncomment this to allow some filetypes regardless of mimetype detection failure (such as mkv)
        // this.handleError('Unable to detect file mimetype in the uploader')
        console.log('unable to detect mimetype in the uploader')
      }



      // Append form data to data obj before passing to flask
      data.append('file', this.uploadInput.files[0]);
      data.append('filename', this.fileName.value);
      data.append('scale', this.state.scale);
      data.append('replacement', this.state.replacement);
      data.append('fileType', fileType)
      console.log('filename w fake ', this.fileName.value)


      let currentFileName = this.fileName.value;
      currentFileName= currentFileName.slice(12);
      currentFileName = currentFileName.split('.')
      let currentFileExt = currentFileName.pop();
      currentFileName = currentFileName[0];
      currentFileName = currentFileName  + '_' + this.state.replacement + '.' + currentFileExt;
      console.log('now filename is ', currentFileName);
      // Processing of the flask response differs depending on the filetype
      // (image or video) in order to render the finished results
      
      console.log('here checking fileType, fileType is: ', fileType)

      if (fileType && fileType === 'video') {
        fetch('/upload', {
          method: 'POST',
          body: data,
          mode: 'cors',
        })
        .then((response) => response.blob())
        .then((blob) => {
          console.log('posting video');
          console.log('url is ', URL.createObjectURL(blob))
          console.log('current file name is ', currentFileName);
          // hide loading animation
          this.setState({ fileProcessing: false })
          // get video url from blob & set video url in app state for rendering
          // uncommented 8-16-21 this.setState({ videoUrl: URL.createObjectURL(blob) })
          this.setState({ videoUrl: currentFileName})
        })
      }
      // if image render processed file
      else if (fileType && fileType === 'image') {
	      console.log('posting image');
        fetch('/upload', { 
	        method: 'POST', 
	        body: data, 
	        mode: 'cors',
	      })
        .then(response => response.blob())
        .then((blob) => {
          let reader = new FileReader();
          // get image url from blob using FileReader
          reader.addEventListener('loadend', () => {
            let contents = reader.result;
            // hide loading animation
            this.setState({ fileProcessing: false })
            //
            this.setState({ imageUrl: contents })
          })
          // pass valid blob to FileReader
          if (blob instanceof Blob) reader.readAsDataURL(blob)
        })
      }
    } else {
      this.handleError('There was an error uploading the files.');
    }
  }

  handleSelectChange = (e) => {
    this.setState({ [e.target.name]: e.target.value });
  }

  render() {

    return (
      <div className="container-fluid customMaxWidth">
        <div className="row">
          <div className="col-12 ">
            <form id="mainForm" onSubmit={this.handleUpload}>
              <p className="pInstructions my-4">1. Choose an image or video to upload by clicking Select File </p>
              <div>
                <input
                  type="file"
                  id="files"
                  accept="video/*, image/*"
                  className="customUploadInput"
                  ref={(ref) => {
                    this.uploadInput = ref;
                    this.fileName = ref;
                  }}
                ></input>
              </div>
              <p className="pInstructions my-4">2. Choose an effect, or upload another face to replace faces in the image with</p>
              <div>
                <input
                  name="effect" 
                  id="effect" 
                  type="radio" 
                  className="replacementType"
                  onChange={this.handleRadioChange}
                  value="effect"
                ></input>
                <label for="dewey">Effect (Emoji, Box, or Blur)</label>
              </div>


              <div>
                <select
                  name="replacement"
                  id="replacement"
                  className="MuiButton-label customSelect"
                  onChange={this.handleSelectChange}
                  defaultValue={this.state.replacement}
                >
                  <option value="solid">box</option>
                  <option value="emoji">emoji</option>
                  <option value="blur">blur</option>
                </select>
              </div>
              <p className="pInstructions my-4">3. Select scale scale resolution for faster processing</p>
              <p className="pInstructions my-4">(NOTE: To increase accuracy try different resolutions)</p>

              <div>
                <select
                  name="scale"
                  id="scale"
                  className="MuiButton-label customSelect"
                  onChange={this.handleSelectChange}
                  defaultValue={this.state.scale}
                >
                  <option value="default">Original Size</option>
                  <option value="1366x768">1366x768</option>
                  <option value="640x360">640x360</option>
                </select>
              </div>
              <p className="pInstructions my-4">4. Click upload to replace faces</p>
              <div>
                <Button
                  variant="contained"
                  type="submit"
                  id="faceReplaceButton"
                  className={`formControlButton`}
                >
                  Upload
               </Button>
                <br />
              </div>
              <p className="pInstructions my-4">5. View Processed media</p>
              {this.state.videoUrl &&
                <video autoPlay controls>
                  <source
                    src={this.state.videoUrl}
                    type="video/mp4">
                  </source>
                Your browser doesn't support HTML5 video tag.
              </video>
              }
              <br />
              {this.state.imageUrl &&
                <img className="processedImg" alt="processedImage" src={this.state.imageUrl} />
              }
              {this.state.fileProcessing &&
                <>
                  <br />
                  <p>File is Processing</p>

                  <div
                    style={{
                      width: "100%",
                      height: "100",
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center"
                    }}
                  >
                    <Loader className="loader" type="ThreeDots" color="#2BAD60" height="100" width="100" />
                    <br />

                  </div>
                </>
              }
              <div className="col-1"></div>
            </form>
          </div>
        </div>
      </div>
    );
  }
}

export default Main;
