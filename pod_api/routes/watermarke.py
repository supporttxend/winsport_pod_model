from fastapi import (
    HTTPException,
    Depends,
    APIRouter,
    status,
    HTTPException,
    Security,
    BackgroundTasks,
    Query,
    Header,
    Request
)
from sqlalchemy.orm import Session
# from session import get_db
import json
import numpy as np
import requests
from pydantic import BaseModel, Field
from typing import Union
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import io
import PyPDF2
from fpdf import FPDF
from typing import List, Union
from quries import get_pod_files_by_id, update_pod_watermark_url
import boto3
import io
from urllib.parse import urlparse
from cloudpathlib import CloudPath
from routes.utils import exception_callback


try:
    BASE_DIR = Path(__file__).resolve().parent

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()

print("water marke", BASE_DIR / "settings.ini")

router = APIRouter()

def resolve_s3_path(url):
    path = urlparse(url)
    s3_key = path.path.lstrip("/")
    s3_uri = f"s3://winsport-node/{s3_key}"
    file_path  = Path(path.path)
    extention = file_path.suffix.lower()
    file_name = file_path.name
    return url, s3_key, s3_uri, extention, file_name


def connect_bucket():
    s3 = boto3.resource('s3', region_name='us-east-1')
    bucket = s3.Bucket('winsport-node')
    return bucket


def get_s3_object(s3_key):
    bucket = connect_bucket()
    response = bucket.Object(s3_key).get()
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("object retrival faild")
        data = response['Body']

        return data
    else:
        print("Error: get_s3_object object is not retrived for {s3_key}")
        return

def del_s3_object(s3_key):
    bucket = connect_bucket()
    response = bucket.Object(s3_key).delete()
    if response['ResponseMetadata']['HTTPStatusCode'] == 204:
        print("object deleted scussfully")
        return
    else:
        print("Error: del_s3_object object is not deleted for {s3_key}")
        return


def get_s3_object_url(s3_key):
    client = boto3.client('s3')
    response = client.generate_presigned_url('get_object', Params={'Bucket': "winsport-node",'Key': s3_key})
    pasred = urlparse(response)
    public_url = f"{pasred.scheme}/{pasred.hostname}{pasred.path}"

    return public_url

def upload_image_to_s3(image, s3_key):
    io_obj = io.BytesIO()
    image.save(io_obj, format="JPEG")
    io_obj.seek(0)

    bucket = connect_bucket()
    bucket.upload_fileobj(io_obj, s3_key)

    return


def new_page(text):
    pdf = FPDF(format='A4') #pdf format
    pdf.add_page() #create new page
    pdf.set_font("Helvetica", size=12)
    with pdf.local_context(text_mode="CLIP"):

        pdf.text(pdf.w - 100, pdf.h - 10, txt=text)
        for r in range(0, 250, 2):  # drawing concentric circles
            pdf.circle(x=pdf.w-r/2, y=pdf.h-r/2, r=r)
    return pdf.output("watermark.pdf")

def apply_watermark_pdf(input_pdf_path, water_mark_text):
    new_page(water_mark_text)
    merged_file = "merged.pdf"

    input_file = open(input_pdf_path,'rb')
    input_pdf = PyPDF2.PdfReader(input_file)
    output = PyPDF2.PdfWriter()

    watermark_file = open("watermark.pdf",'rb')
    watermark_pdf = PyPDF2.PdfReader(watermark_file)

    for i in range(input_pdf.pages.length_function()):
        print(i)
        page = input_pdf.pages.get_function(i)
        page.merge_page(watermark_pdf.pages.get_function(0))
        output.add_page(page)

    with open(merged_file, 'wb') as file:
        output.write(file)



def apply_watermark_image(s3_key,file_name, s3_uri, text):

    if s3_key:
        byte_image = get_s3_object(s3_key)
        im = Image.open(byte_image).convert("RGB")
        width, height = im.size
        draw = ImageDraw.Draw(im)
        text = str(text)
        font = ImageFont.load_default()
        textwidth, textheight = draw.textsize(text, font)
        margin = 10
        x = width - textwidth - margin
        y = height - textheight - margin
        black = (3, 8, 12, 0)
        draw.text((x, y), text, fill=black, font=font)
        s3_new_key = f"{Path(s3_key).parent}/water_marked_{file_name}"
        upload_image_to_s3(im, s3_new_key)
        url = get_s3_object_url(s3_new_key)
        # im.save(BASE_DIR.parent.parent / f"data/watermark_{file_name}")
        # del_s3_object(s3_uri)

        return url

    return

def apply_watermark(pod_id):
    file_list = get_pod_files_by_id(pod_id)

    for url in file_list:
        if not url:
            continue
        url, s3_key, s3_uri, extention, file_name = resolve_s3_path(url)
        file_type_resp = file_type(extention)
        if file_type_resp == "image":
            url = apply_watermark_image(s3_key=s3_key, file_name=file_name, s3_uri=s3_uri, text=pod_id)
        if file_type_resp == "pdf":
            print("applying water mark on pdf")
            url = apply_watermark_pdf(s3_key=s3_key, file_name=file_name, s3_uri=s3_uri, text=pod_id)

        if "POD" in url:
            data = {"podPath": url}
        if "BOL" in url:
            data = {"bolPath": url}

        update_pod_watermark_url(pod_id, data)

def file_type(extention):
    file_types = {
        ".jpg": "image",
        ".jpeg": "image",
        ".png": "image",
        ".pdf": "pdf",
    }
    if extention not in file_types:
        exception_callback(status.HTTP_400_BAD_REQUEST,
                           "File Type Missmatched",
                           {"data": f"{extention}", "message": "File Type Missmatched" }
                           )

    else:
        if file_types[extention] == "image":
            return "image"

        if file_types[extention] == "pdf":
            return "pdf"

@router.get("/")
def water_marking(pod_id, bg_task: BackgroundTasks):
    bg_task.add_task(apply_watermark, pod_id)
    return {"status": status.HTTP_200_OK, "data": "Content_Type"}