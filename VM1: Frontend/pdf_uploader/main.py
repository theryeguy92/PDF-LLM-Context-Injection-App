import os
import shutil
import time
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from PyPDF2 import PdfReader
from kafka import KafkaProducer
import json
import httpx
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not DATABASE_URL or not KAFKA_BROKER_URL or not KAFKA_TOPIC:
    raise HTTPException(status_code=500, detail="Missing required environment variables.")

# FastAPI Instance
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="uploads/templates")

# Database Connection
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define Tables
pdf_files = Table(
    "pdf_files", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("file_name", String(255), nullable=False),
    Column("upload_date", String(255), nullable=False),
    Column("context", Text, nullable=True),
)

user_conversations = Table(
    "user_conversations", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_query", Text, nullable=False),
    Column("llm_response", Text, nullable=False),
    Column("timestamp", String(255), default=datetime.utcnow),
)

metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Kafka Configuration
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Parse PDF File
def parse_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        return None

# Home Route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("VM1HTMLFramework.html", {"request": request})

# Endpoint to upload PDF
@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # Save file locally
    file_location = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse the PDF and extract context
    context = parse_pdf(file_location)

    # Send data to Kafka
    message = {
        "file_name": file.filename,
        "upload_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "context": context
    }
    producer.send(KAFKA_TOPIC, message)
    producer.flush()

    # Save metadata to database
    db = SessionLocal()
    db.execute(
        pdf_files.insert().values(
            file_name=file.filename,
            upload_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            context=context,
        )
    )
    db.commit()
    db.close()

    return {"status": "File sent to Kafka successfully", "file_name": file.filename}

# Endpoint to interact with the chatbot
@app.post("/chatbot/")
async def chatbot(request: Request):
    data = await request.json()
    query = data.get("query", "")

    # Retrieve context from MySQL
    db = SessionLocal()
    result = db.execute(text("SELECT context FROM pdf_files ORDER BY upload_date DESC LIMIT 1"))
    context_row = result.fetchone()
    db.close()

    if not context_row or not context_row[0]:
        return JSONResponse(content={"answer": "No context available from uploaded files."})

    context = context_row[0]

    # Send query and context to VM3 (LLM)
    llm_url = "http://172.31.15.130:5000/generate/"
    payload = {"prompt": f"Context: {context[:500]}\n\nQuestion: {query}", "max_length": 200}

    retries = 3
    answer = "No valid response from LLM."
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(llm_url, json=payload)
                response_data = response.json()
                if "generated_text" in response_data:
                    answer = response_data["generated_text"].strip()
                    break
        except httpx.RequestError as e:
            logger.error(f"Error communicating with LLM: {e}")
            answer = f"Error communicating with LLM: {e}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            answer = f"Unexpected error: {e}"
        time.sleep(5)

    # Save the conversation in MySQL
    db = SessionLocal()
    db.execute(
        user_conversations.insert().values(
            user_query=query,
            llm_response=answer,
        )
    )
    db.commit()
    db.close()

    return JSONResponse(content={"answer": answer})
