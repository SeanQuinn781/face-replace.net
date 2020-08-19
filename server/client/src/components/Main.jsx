import React from 'react'
import { Button } from '@material-ui/core';
import Loader from 'react-loader-spinner';
import MimeType from 'mimetype';

class Main extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      mediaURL: "Pending Upload",
      fileOptions: "blur",
      fileProcessing: false,
      videoUrl: false,
      imageUrl: false,
    };

    this.handleUpload = this.handleUpload.bind(this);
    this.handleSelect = this.handleSelect.bind(this);
  }

  handleUpload(e) {

    e.preventDefault();
    const data = new FormData();

    if (this.uploadInput.files[0].name) {

      // Display loading animation until file has been sent to backend and finished processing
      this.setState({ fileProcessing: true })

      // Check mimetype, determine if upload media is an img or video
      let mType = MimeType.lookup(this.uploadInput.files[0].name)
      mType = mType.split('/')[0] === 'image' ? 'image' : 'video'

      data.append('file', this.uploadInput.files[0]);
      data.append('filename', this.fileName.value);
      data.append('fileOptions', this.state.fileOptions);
      data.append('fileType', mType)

      if (mType && mType === 'video') {
        fetch('http://localhost:5000/upload', { method: 'POST', body: data })
          .then((response) => response.blob())
          .then((blob) => {
            // hide loading animation
            this.setState({ fileProcessing: false })
            // get video url from blob & set video url in app state for rendering
            this.setState({ videoUrl: URL.createObjectURL(blob) })
          })
      }
      // if image render processed file
      else if (mType && mType === 'image') {
        fetch('http://localhost:5000/upload', { method: 'POST', body: data })
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
    }
  }

  handleSelect(e) {
    const fileOptions = e.target.value;
    this.setState({ fileOptions: fileOptions });
  }

  render() {

    return (
      <div className="container-fluid customMaxWidth">
        <div className="row">
          <div className="col-10 offset-1">
            <h3 id="logoHeader">Face-Replace</h3>
            <form id="mainForm" onSubmit={this.handleUpload}>
              <p className="pInstructions">1. Choose an image or video to upload by clicking Select File </p>
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
                />
              </div>
              <br />
              <p className="pInstructions mb-4">2. Choose an effect to replace faces with</p>
              <div>
                <select
                  name="replacement"
                  id="replacement"
                  className="MuiButton-label customSelect"
                  value={this.state.fileOptions}
                  onChange={this.handleSelect}
                >
                  <option value="solid">box</option>
                  <option value="blur">blur</option>
                  <option value="emoji" defaultValue="selected">emoji</option>
                </select>
              </div>
              <br />
              <p className="pInstructions mb-2 mt-2">3. Click UPLOAD to replace faces</p>
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
              <p className="pInstructions mb-2 mt-2">4. View Processed media</p>
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
                  <p>File is Processing</p>
                  <br />
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
