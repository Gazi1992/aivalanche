import json
import logging
# from kafka import KafkaConsumer

from asyncio import create_task, TimeoutError
import asyncio
from aiokafka import AIOKafkaConsumer
import aiokafka
import time
import os

from kafka_consumer.config import topics
from kafka_producer.kafka_producer import start_simulation, send_json
from simulation.ngspice.parameter_set import parameter_set


# BROKERS = 'defb.kafka:29092'


BROKERS = "kafkafb:9093"
# Kafka topics to consume from


worker_connected = False

async def consumer_with_timeout(timeout):
    consumer = AIOKafkaConsumer(
        *topics, bootstrap_servers=BROKERS, enable_auto_commit=True, group_id="new_connections", auto_offset_reset="earliest",consumer_timeout_ms=1000
    )

    try:
        start_time = time.perf_counter()
        # Create task to monitor timer
        timeout_task = asyncio.create_task(asyncio.sleep(timeout))

        async def monitor_timeout():
            try:
                await timeout_task
                print("Timeout reached. Closing consumer...")
                await consumer.stop()
            except asyncio.CancelledError:
                pass
        
        monitor_task = asyncio.create_task(monitor_timeout())
        print("Before starting consumer")

        await consumer.start()
        try:
            async for msg in consumer:  # Iterate over incoming messages
                if msg is None:
                    # No message received within timeout, consider handling timeout here
                    print("No message received within timeout")
                    break
                 # Process message logic here
                event_data = msg.value.decode('utf-8')
                data = json.loads(event_data)
                event_type = data["event"]
                print(event_type)
                print("Message Offset:", msg.offset)
                print("Time elapsed: ", time.perf_counter() - start_time)
                # if time.perf_counter() - start_time >= 10:
                #     print("Consumer reached 30 second limit. Closing...")
                #     break
                await process_event(event_type, data)
                print(f"Received message: {msg.value.decode()}")
                await consumer.commit()  # Commit the message to mark it as processed

                if consumer._closed:
                    print("Consumer closed")
                    monitor_task.cancel()

                    # break  # Exit the loop after processing a message
        # Rest of your message processing logic here
        except aiokafka.errors.KafkaError as e:
          print("Topic 'NEW_WORKER' does not exist yet. Retrying...",e)

        finally:
            await consumer.stop()
            print("After stopping consumer")
              
    except Exception as e:
            print("Timeout reached. Closing consumer...",e)
            pass

    if monitor_task.done():
        print("Monitor task done")



async def consume():
    consumer = AIOKafkaConsumer(
        *topics, bootstrap_servers=BROKERS, enable_auto_commit=True, group_id="new_connections", auto_offset_reset="earliest"
    )

    await consumer.start()
    try:
        async for msg in consumer:  # Iterate over incoming messages
            if msg is None:
                # No message received within timeout, consider handling timeout here
                continue
            # Process message logic here
            event_data = msg.value.decode('utf-8')
            data = json.loads(event_data)
            event_type = data["event"]
            print(event_type)
            print("Message Offset:", msg.offset)
            await process_event(event_type, data)
            print(f"Received message: {msg.value.decode()}")
            await consumer.commit()  # Commit the message to mark it as processed
            # break  # Exit the loop after processing a message
    except aiokafka.errors.KafkaError as e:
            print("Topic 'NEW_WORKER' does not exist yet. Retrying...",e)
    finally:
        await consumer.stop()
        print("After stopping consumer")


async def process_event(event_type, data):
    """
    This function is a placeholder for your actual event processing logic.
    You can modify it to handle the event data as needed.
    """
    async def process_task(event_type, data):
        match event_type:
            case "new_worker_confirmation":
                print("Processing 'new_worker_confirmation' event")
                logging.info("Processing 'new_worker_confirmation' event")
                process_message_and_save_topic(data)

            case "files_received_successfully":
                print("Processing 'files_received_successfully' event")
                logging.info("Processing 'files_received_successfully' event")
                await start_simulation(data["new_topic"],"run_simulation")

            case "simulation_iteration_complete":
                print("Processing 'simulation_iteration_complete' event")
                logging.info("Processing 'simulation_iteration_complete' event")
                await send_json(data["new_topic"],parameter_set,"new_parameters")
                await start_simulation(data["new_topic"],"run_simulation")
               
            case _:
                print("Unknown event type:", event_type)
    await asyncio.sleep(1)
    await process_task(event_type, data)




def process_message_and_save_topic(message):
 
    # Extract the new_topic value
    new_topic = message.get("new_topic")
    
    if new_topic:
        print("After processing", new_topic)
        save_new_topic_into_file(new_topic)
        print("New topic saved to file")

def save_new_topic_into_file(new_topic):

     # Get the path of the file where the function is defined
    current_file_path = __file__

  # Extract the directory path from the file path
    function_dir = os.path.dirname(current_file_path)

  # Define the file path relative to the function's directory
    new_topics_file = os.path.join(function_dir, 'config.py')

      # Check if the new topic already exists in the list
    if new_topic not in topics:
        topics.append(new_topic)
    # Open the file in append mode and write the new topic
    try:
         # Optionally write the updated config to a file (consider performance implications)
        with open(new_topics_file, 'w') as file:  # Overwrites the entire file
            file.writelines([f"topics = {topics}\n"])  # Write the updated list
    except FileNotFoundError:
        print(f"Error: File '{new_topics_file}' not found. Creating a new one.")
        # Consider adding logic to create the file here if needed

if __name__ == '__main__':
    asyncio.run(consumer_with_timeout(120))

    
