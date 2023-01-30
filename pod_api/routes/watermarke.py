import io
from io import BytesIO
# from session import get_db
import json
from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse

import PyPDF2
from fastapi import (APIRouter, BackgroundTasks, Depends, Header,
                     HTTPException, Query, Request, Security, status)
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config import settings
from quries import get_pod_files_by_id, update_pod_watermark_url
from routes.quries_s3 import (del_s3_object, get_s3_object, get_s3_object_url,
                              upload_image_to_s3, upload_pdf_to_s3)
from routes.utils import exception_callback
import time

try:
    BASE_DIR = Path(__file__).resolve().parent

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()

print("water marke", BASE_DIR / "settings.ini")


S3_BUCKET_NODE = settings.S3_BUCKET_NODE




router = APIRouter()

def resolve_s3_path(url):
    path = urlparse(url)
    s3_key = path.path.lstrip("/")
    s3_uri = f"s3://{S3_BUCKET_NODE}/{s3_key}"
    file_path  = Path(path.path)
    extention = file_path.suffix.lower()
    file_name = file_path.name
    return url, s3_key, s3_uri, extention, file_name



def new_page(text):
    pdf = FPDF(format='A4') #pdf format
    pdf.add_page() #create new page
    pdf.set_font("Helvetica", size=12)
    with pdf.local_context(text_mode="CLIP"):

        pdf.text(pdf.w - 100, pdf.h - 10, txt=text)
        for r in range(0, 250, 2):  # drawing concentric circles
            pdf.circle(x=pdf.w-r/2, y=pdf.h-r/2, r=r)
    return pdf.output("watermark.pdf")

def apply_watermark_pdf(s3_key, text):
    # text = "umer javed is a good boy"
    # s3_key = "c7e025aa-d96e-4bcc-afa6-9d9ddf41f819/bol/Dev Onboarding.pdf"
    new_page(text)
    # merged_file = "merged.pdf"
    # s3_key = "c7e025aa-d96e-4bcc-afa6-9d9ddf41f819/bol/water_marked_1673936161_umer javed is a good boy.pdf"
    byte_pdf = get_s3_object(s3_key)
    # input_file = open(input_pdf_path,'rb')
    # input_file = byte_pdf.read()
    input_pdf = PyPDF2.PdfReader(io.BytesIO(byte_pdf.read()))
    output = PyPDF2.PdfWriter()

    watermark_file = open("watermark.pdf",'rb')
    watermark_pdf = PyPDF2.PdfReader(watermark_file)

    for i in range(input_pdf.pages.length_function()):
        # print(i)
        page = input_pdf.pages.get_function(i)
        page.merge_page(watermark_pdf.pages.get_function(0))
        output.add_page(page)

    # local pdf save
    # with open(merged_file, 'wb') as file:
    #     output.write(file)

    # save to s3
    s3_new_key = f"{Path(s3_key).parent}/water_marked_{int(time.time())}_{text}.pdf"
    upload_pdf_to_s3(output, s3_key=s3_new_key)

    url = get_s3_object_url(s3_new_key)
    del_s3_object(s3_key)

    return url

def file_type(extention):
    file_types = {
        ".jpg": "image",
        ".jpeg": "image",
        ".png": "image",
        ".pdf": "pdf",
    }
    if extention not in file_types:
        exception_callback(
            status.HTTP_400_BAD_REQUEST,
            "File Type Missmatched",
            {"data": f"{extention}", "message": "File Type Missmatched"}
            )

    else:
        if file_types[extention] == "image":
            return "image"

        if file_types[extention] == "pdf":
            return "pdf"



def apply_watermark_image(s3_key, text):

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
        s3_new_key = f"{Path(s3_key).parent}/water_marked_{int(time.time())}_{text}.jpeg"
        upload_image_to_s3(im, s3_new_key)
        url = get_s3_object_url(s3_new_key)
        # im.save(BASE_DIR.parent.parent / f"data/watermark_{file_name}")
        del_s3_object(s3_key)

        return url

def apply_watermark(pod_id):
    file_list = get_pod_files_by_id(pod_id)
    new_file_urls = {}
    print("file_list ----------->", file_list)
    for url in file_list:
        if not url:
            continue
        url, s3_key, s3_uri, extention, file_name = resolve_s3_path(url)
        print(url, s3_key, s3_uri, extention, file_name)
        file_type_resp = file_type(extention)
        if file_type_resp == "image":
            url = apply_watermark_image(s3_key=s3_key, text=pod_id)
        if file_type_resp == "pdf":
            print("applying water mark on pdf")
            url = apply_watermark_pdf(s3_key=s3_key, text=pod_id)

        if "pod" in url:
            # data = {"podPath": url}
            new_file_urls["podPath"] = url
            new_file_urls['isWaterMarked'] = True
        if "bol" in url:
            # data = {"bolPath": url}
            new_file_urls["bolPath"] = url
            new_file_urls['isWaterMarked'] = True
        if "invoice" in url:
            # data = {"invoicePath": url}
            new_file_urls["invoicePath"] = url
            new_file_urls['isWaterMarked'] = True

    update_pod_watermark_url(pod_id, new_file_urls)






@router.get("")
def water_marking(pod_id, bg_task: BackgroundTasks):
    bg_task.add_task(apply_watermark, pod_id)
    return {"status": status.HTTP_200_OK, "data": "Content_Type"}