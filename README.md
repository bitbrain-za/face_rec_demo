# Face Recognition Demo

## Usage

### Deepstack container

`docker run -d --runtime nvidia -e VISION-FACE=True -p 8080:5000 -e MODE=Low deepquestai/deepstack:jetpack`

### Detector

`pip3 install -r requirements_detector.txt`
`python3 detect.py -i 'rtsp://<address>/<path>'`

### Registration

Easiest to run on a PC (streamlit and jetpack don't play well)

`pip3 install -r requirements_detector.txt`
`streamlit run face_reg.py`