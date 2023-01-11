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
from pydantic import BaseModel, Field
from typing import Union
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import PyPDF2
from fpdf import FPDF
from typing import List, Union
from quries import get_pod_files_by_id, update_pod_watermark_url
import io
from urllib.parse import urlparse
from routes.utils import exception_callback
from config import settings
from routes.quries_s3 import upload_image_to_s3, del_s3_object, get_s3_object, get_s3_object_url


try:
    BASE_DIR = Path(__file__).resolve().parent

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()

print("water marke", BASE_DIR / "settings.ini")




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

def apply_watermark_pdf(input_pdf_path, text):
    new_page(text)
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
        del_s3_object(s3_uri)

        return url

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




@router.get("/")
def water_marking(pod_id, bg_task: BackgroundTasks):
    bg_task.add_task(apply_watermark, pod_id)
    return {"status": status.HTTP_200_OK, "data": "Content_Type"}