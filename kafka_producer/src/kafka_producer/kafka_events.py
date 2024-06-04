from kafka_producer.kafka_init import send_event
from datetime import datetime
import uuid



async  def send_get_files_to_every_worker(type, file_id):    
    # kafka topic
    KAFKA_TOPIC = "every_worker_topic"
    print(f"Sending event to {KAFKA_TOPIC}")
    
    # send event to kafka
    data = dict(
        event = "get_files",
        type = type,
        file_id = file_id,
        event_id=str(uuid.uuid4()),
        date_created=str(datetime.utcnow())
    )
    await send_event(KAFKA_TOPIC,  data)

async def send_event_to_worker(KAFKA_TOPIC, event):

    # send event to kafka
    data = dict(
        event = event,
        event_id=str(uuid.uuid4()),
        date_created=str(datetime.utcnow())
    )
    print(f"Sending event to {KAFKA_TOPIC}")
    await send_event(KAFKA_TOPIC,  data)

async def send_json_to_worker(KAFKA_TOPIC, json_data, event):
    # send event to kafka
    data = dict(
        event = event,
        parameters = json_data,
        date_created=str(datetime.utcnow())
    )
    print(f"Sending event to {KAFKA_TOPIC}")
    await send_event(KAFKA_TOPIC,  data)

