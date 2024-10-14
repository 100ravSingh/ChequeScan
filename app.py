#/usr/bin/python
import google.generativeai as genai
import PIL.Image
from PIL import Image
from io import BytesIO
import os
import cv2
import streamlit as st
import numpy as np
import toml
import zipfile
import json
import shutil
import crop as cp
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime
from dotenv import load_dotenv
from openpyxl.workbook import Workbook
load_dotenv()


# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(model_name="gemini-1.5-flash")
#model = genai.GenerativeModel(model_name="gemini-1.5-pro")
# img = PIL.Image.open('path/to/image.png')

if 'customer' not in st.session_state:
  st.session_state.customer = []
if 'cheque_data' not in st.session_state:
  st.session_state.cheque_data = {}

#Load prompt
config = toml.load('prompt.toml')
input_prompt = config['prompt1']['input_prompt']

upload_directory = "input_images"
if not os.path.exists(upload_directory):
  os.makedirs(upload_directory)

signature_directory = "sign_images"
if not os.path.exists(signature_directory):
  os.makedirs(signature_directory)

cheque_directory = "cheque_images"
if not os.path.exists(cheque_directory):
  os.makedirs(cheque_directory)

#Streamlit frontend

# st.title("Cheque book Extraction using AI") 
st.markdown("""
<h1 style = 'text-align: center;
            color: black;
            font-size: 40px;
            width: 100%;
            background-color: lightgray;
            padding: 10px;
            margin-bottom: 10px'>
            Cheque book Extraction using AI
            </h1>
          """,
          unsafe_allow_html=True
)


#upload file
# if st.button("Upload Single Image"):
single_image_file = st.file_uploader("choose an image...", type=["jpg","jpeg","png"])

# upload zip
# if st.button("Upload Zip file"):
zip_file = st.file_uploader(" \n choose a zip file containing images", type=["zip"])



if single_image_file is not None:
  image = Image.open(single_image_file)
  st.image(image, caption='Upload image.',use_column_width=True)
  st.write("")

  if st.button("Cheque box"):
    response = model.generate_content([input_prompt, image])
    st.success(response.text)
    st.session_state.cheque_data = response.text.strip(" ```json")
    st.session_state.cheque_data = json.loads(st.session_state.cheque_data)
    cheque_name = f'{st.session_state.cheque_data["Cheque number"]}_signature.jpg'
    down_path = os.path.join(cheque_directory,cheque_name)
    # image.save(down_path)
    #For Deployment
    image.convert('RGB').save(down_path)

    cp_image = cp.preprocess_image(image)
    cp_image = cp.sharpen_image(cp_image)
    fname = f'{st.session_state.cheque_data["Cheque number"]}_signature.jpg'
    save_path = os.path.join(signature_directory,fname)
    cp_image = Image.fromarray(cp_image)
    cp_image.save(save_path)
    st.session_state.cheque_data["Cheque_img"] = down_path
    st.session_state.cheque_data["Sign_img"] = save_path
    st.session_state.customer.append(st.session_state.cheque_data)


if zip_file is not None:
  with zipfile.ZipFile(zip_file,'r') as zip_ref:
    zip_ref.extractall(upload_directory)
  st.success("Image have been uploaded successfully!")

  if st.button("Cheque Tool"):
    with zipfile.ZipFile(zip_file,'r') as zip_ref:
      images_files = [f for f in zip_ref.namelist() if f.endswith(('.png','.jpg','.jpeg'))]
      for images_file in images_files:
        with zip_ref.open(images_file) as img_file:
          img_data = img_file.read()
        image = Image.open(BytesIO(img_data))
        response = model.generate_content([input_prompt, image])
        st.session_state.cheque_data = response.text.strip(" ```json")
        st.session_state.cheque_data = json.loads(st.session_state.cheque_data)
        cheque_name = f'{st.session_state.cheque_data["Cheque number"]}_signature.jpg'
        down_path = os.path.join(cheque_directory,cheque_name)
        # image.save(down_path)
        #For Deployment
        image.convert('RGB').save(down_path)

        cp_image = cp.preprocess_image(image)
        cp_image = cp.sharpen_image(cp_image)
        fname = f'{st.session_state.cheque_data["Cheque number"]}_signature.jpg'
        save_path = os.path.join(signature_directory,fname)
        cp_image = Image.fromarray(cp_image)
        cp_image.save(save_path)
        st.session_state.cheque_data["Cheque_img"] = down_path
        st.session_state.cheque_data["Sign_img"] = save_path
        st.session_state.customer.append(st.session_state.cheque_data)
      st.success("Batch operations success")

# if customer:
if st.session_state.customer:
  if st.button("Ready for Download"):
    def create_zip_with_folder_and_file(zip_name,folder1,folder2,filename):
      with zipfile.ZipFile(zip_name,'w') as zipf:
        for root, dirs, files in os.walk(folder1):
          for file in files:
            file_path = os.path.join(root,file)
            arcname = os.path.join(folder1,os.path.relpath(file_path,folder1))
            zipf.write(file_path,arcname)
    
        for root, dirs, files in os.walk(folder2):
          for file in files:
            file_path = os.path.join(root,file)
            arcname = os.path.join(folder2,os.path.relpath(file_path,folder2))
            zipf.write(file_path,arcname)

        zipf.write(filename,os.path.basename(filename))



    def cleanup():
      if os.path.exists(upload_directory):
        shutil.rmtree(upload_directory)
      if os.path.exists(cheque_directory):
        shutil.rmtree(cheque_directory)
      if os.path.exists(signature_directory):
        shutil.rmtree(signature_directory)
      if os.path.exists(excel_file_name):
        os.remove(excel_file_name)
      if os.path.exists(zip_output):
        os.remove(zip_output)
        st.session_state.customer = []
        st.session_state.cheque_data = {}
      
      

    df = pd.DataFrame(st.session_state.customer)
    
    excel_file_name = 'cheque_table.xlsx'
    df.to_excel(excel_file_name,index=False)
  
    zip_output = 'Result_data.zip'
    create_zip_with_folder_and_file(zip_output,cheque_directory,signature_directory,excel_file_name)
  
    with open(zip_output, 'rb') as f:
      st.download_button(label="Download Output in zip (Table, cheque & sign folders)",
      data = f.read(),
      file_name = zip_output,
      mime = 'application/zip')
      cleanup()


# Footer section
footer = """
  <style>
  .footer { 
      position: fixed;
      left: 0;
      bottom: 0;
      width: 100%;
      background-color: lightgray;
      color: black;
      text-align: center;
      padding: 10px;
      }
      a {
        color: blue;
        text-decoration: none;
      }
      a:hover {
        text-decoration: underline;
      }
      </style>
      <div class="footer">
        <p>Designed by Sourav Singh © 2024 | Contact:<a href="https://100ravsingh.github.io/" target = "_blank" >Visit Here!!</a> | <a href="https://100ravsingh.github.io/ChequeScan/" target = "_blank">Developer</a></p>
      </div>
      """

components.html(footer, height=100)
