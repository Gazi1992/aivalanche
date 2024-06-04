import json
import time
import uuid
import logging
from datetime import datetime
from kafka import KafkaProducer
from kafka_producer.kafka_producer import send_event

logging.basicConfig(level=logging.INFO)

# create kafka topic
ORDER_KAFKA_TOPIC = "order_processed"
ORDER_LIMIT = 1

# # producer = KafkaProducer(bootstrap_servers="kafka:9092")
# print("Producer started...", producer)
# print("Connected to kafka broker...", producer.bootstrap_connected())
# logging.info("Producer started...")



if __name__ == '__main__':
    logging.info("Generating orders...")
 
    
    for order in range(ORDER_LIMIT):
        # data = create_orders()
        # send orders to kafka topic
        data_1 = dict(
            event = "EVERY_WORKER_TOPIC",
            order_id=str(uuid.uuid4()),
            date_created=str(datetime.utcnow())
        )

        data_2 = dict(
            event = "run_simulation",
            order_id=str(uuid.uuid4()),
            date_created=str(datetime.utcnow())
        )
        send_event("worker_1", data=data_2)
        send_event("every_worker_topic", data=data_1)
        logging.info(f"Done creating order ...{order}")
        # time.sleep(1)
