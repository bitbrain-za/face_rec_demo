import streamlit as st
from PIL import Image
from deepstack_sdk import ServerConfig, Face

st.title("SIG Face Registration")
DEFAULT_DS_SERVER = "http://localhost:80"

config = ServerConfig(DEFAULT_DS_SERVER)
face = Face(config)

ds_server = st.text_input(label="Enter SIG address", value=DEFAULT_DS_SERVER)
if ds_server != DEFAULT_DS_SERVER:
    print("Setting server to " + ds_server)
    config = ServerConfig(ds_server)
    face = Face(config)

st.header("Deepstack Face registration")
INSTRUCTION = "First enter the name to register below then load the image"
ENTER_MESSAGE = "Enter name here"
face_name = st.text_input(label=INSTRUCTION, value=ENTER_MESSAGE)
if face_name != ENTER_MESSAGE:
    st.write(f"Registering {face_name}")
    print("Registering {face_name}")
    img_file_buffer_register = st.file_uploader(
        "Upload an image to register", type=["png", "jpg", "jpeg"]
    )
    if img_file_buffer_register is not None:
        pil_image_register = Image.open(img_file_buffer_register)
        response = face.registerFace(images=[pil_image_register],userid=face_name)
        st.write(response)
        face_name = ENTER_MESSAGE


if st.button('List Registered'):
    response = face.listFaces()
    for obj in response:
        st.write(obj)
        print(obj)

if st.button('Clear Registered'):
    response = face.listFaces()
    for obj in response:
        face.deleteFace(obj)
    st.write("Done")