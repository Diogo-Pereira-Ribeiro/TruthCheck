import json
import os
import time
import pika

WORKER_ID = os.getenv("WORKER_ID", "worker")
QUEUE_NAME = os.getenv("QUEUE_NAME", "news.analysis.worker1")
RABBITMQ_URL = os.environ["RABBITMQ_URL"]


def connect():
    params = pika.URLParameters(RABBITMQ_URL)
    while True:
        try:
            connection = pika.BlockingConnection(params)
            print(f"[{WORKER_ID}] Ligado ao RabbitMQ.", flush=True)
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"[{WORKER_ID}] RabbitMQ indisponível. Nova tentativa em 3 segundos.", flush=True)
            time.sleep(3)


def handle_message(channel, method, properties, body):
    try:
        task = json.loads(body.decode("utf-8"))
        print(f"[{WORKER_ID}] Recebida análise {task['analysis_id']}: {task['title']}", flush=True)
        # Nesta etapa, o Worker confirma a receção. A análise será implementada depois.
        channel.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[{WORKER_ID}] Tarefa confirmada.", flush=True)
    except Exception as exc:
        print(f"[{WORKER_ID}] Erro: {exc}", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    connection = connect()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_message)
    print(f"[{WORKER_ID}] À espera na fila {QUEUE_NAME}.", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
