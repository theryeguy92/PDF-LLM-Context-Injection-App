from kafka import KafkaConsumer
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Text
from sqlalchemy.orm import sessionmaker
import json

# Kafka Configuration
KAFKA_BROKER_URL = "172.31.9.51:9092"
KAFKA_TOPIC = "pdf_data"

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER_URL,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    group_id="pdf_processor"
)

# Database Connection
DATABASE_URL = "mysql+mysqlconnector://admin:password@127.0.0.1/pdf_rag_app"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define Table
pdf_files = Table(
    "pdf_files", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("file_name", String(255), nullable=False),
    Column("upload_date", String(255), nullable=False),
    Column("context", Text, nullable=True),
)

metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Consume messages from Kafka and insert into database
for message in consumer:
    data = message.value
    db = SessionLocal()
    db.execute(pdf_files.insert().values(
        file_name=data["file_name"],
        upload_date=data["upload_date"],
        context=data["context"]
    ))
    db.commit()
    db.close()
