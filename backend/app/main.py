import json
import os
import uuid
from datetime import datetime, timezone

import pika
import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DATABASE_URL = os.environ["DATABASE_URL"]
RABBITMQ_URL = os.environ["RABBITMQ_URL"]
QUEUES = ["news.analysis.worker1", "news.analysis.worker2", "news.analysis.worker3"]

app = FastAPI(title="TruthCheck API", version="0.1.0")


class AnalysisRequest(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    content: str = Field(min_length=20, max_length=30000)
    url: str | None = None
    language: str = Field(default="pt", pattern="^(pt|en)$")


def db():
    return psycopg.connect(DATABASE_URL)


def init_database():
    with db() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS analyses ("
            "analysis_id UUID PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL, "
            "url TEXT, language VARCHAR(2) NOT NULL, status VARCHAR(20) NOT NULL, "
            "created_at TIMESTAMPTZ NOT NULL)"
        )


def publish_tasks(payload):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    try:
        channel = connection.channel()
        for queue in QUEUES:
            channel.queue_declare(queue=queue, durable=True)
            channel.basic_publish(
                exchange="", routing_key=queue,
                body=json.dumps(payload).encode("utf-8"),
                properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
            )
    finally:
        connection.close()


@app.on_event("startup")
def startup():
    init_database()


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "truthcheck-backend"}


@app.post("/api/analyses", status_code=202)
def create_analysis(request: AnalysisRequest):
    analysis_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)
    payload = {
        "analysis_id": analysis_id, "title": request.title,
        "content": request.content, "url": request.url, "language": request.language,
    }
    try:
        with db() as conn:
            conn.execute(
                "INSERT INTO analyses "
                "(analysis_id, title, content, url, language, status, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (analysis_id, request.title, request.content, request.url,
                 request.language, "processing", created_at),
            )
        publish_tasks(payload)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Falha ao iniciar análise: {exc}")
    return {"analysis_id": analysis_id, "status": "processing"}


@app.get("/api/analyses/{analysis_id}")
def get_analysis(analysis_id: str):
    try:
        parsed_id = uuid.UUID(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")
    with db() as conn:
        row = conn.execute(
            "SELECT analysis_id, title, url, language, status, created_at "
            "FROM analyses WHERE analysis_id = %s", (parsed_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    return {
        "analysis_id": str(row[0]), "title": row[1], "url": row[2],
        "language": row[3], "status": row[4], "created_at": row[5].isoformat(),
    }
