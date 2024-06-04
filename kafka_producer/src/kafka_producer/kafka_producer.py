from kafka_producer.kafka_events import send_event_to_worker, send_json_to_worker
import asyncio


async def start_simulation(new_topic, event):
    print("Starting simulation")
    await send_event_to_worker(new_topic, event)
    print("Simulation started")

async def send_json(new_topic,data, event):
    print("Sending json")
    await send_json_to_worker(new_topic, data, event)
    print("Json sent")