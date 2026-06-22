# =================================================================
#  Backend Data Collector Service - LSS Project
#  This script consumes IoT sensor payloads via MQTT and persists
#  the historical data into a relational PostgreSQL database.
# =================================================================

import paho.mqtt.client as mqtt
import psycopg2
import json
import os
import time
import logging

# Setup structural application logging to monitor system state and data intake
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fetch application environment configs dynamically injected by Docker Compose
DB_HOST = os.getenv("DB_HOST", "database")
DB_NAME = os.getenv("DB_NAME", "iot_db")
DB_USER = os.getenv("DB_USER", "iot_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "iot_password")

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", 1883))
TOPICS = ["sensors/temperature", "sensors/humidity", "sensors/air_quality"]

def get_db_connection():
    """
    Attempts to map a stable connection handle to the database with a built-in
    retry mechanism to handle initial multi-container startup race conditions.
    """
    attempts = 5
    while attempts > 0:
        try:
            # Bind low-level network socket connection to PostgreSQL server
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            return conn
        except psycopg2.OperationalError:
            # Catch transient database availability drops and wait
            logger.warning(f"Database target unreachable. Retrying in 5 seconds... ({attempts} attempts left)")
            attempts -= 1
            time.sleep(5)
    
    logger.error("Database connection failure threshold exceeded. Aborting pipeline execution.")
    raise Exception("Critical engine failure: Database unavailable.")

def on_message(client, userdata, message):
    """
    Asynchronous event hook triggered whenever a telemetry packet lands on a subscribed topic.
    """
    conn = None
    try:
        # Decode and transform incoming binary array stream into native JSON layout
        payload = json.loads(message.payload.decode())
        sensor_id = payload["sensor_id"]
        sensor_type = payload["sensor_type"]
        value = payload["value"]
        timestamp = payload["timestamp"] # Tracking sensor-side synchronization timestamps

        # Spin up database context handles
        conn = get_db_connection()
        
        # Open a secure context manager to handle database cursor lifecycle automatically
        with conn.cursor() as cursor:
            # Format and dispatch normalized structured insert operations securely
            cursor.execute(
                "INSERT INTO sensor_data (sensor_id, sensor_type, value, timestamp) VALUES (%s, %s, %s, %s)",
                (sensor_id, sensor_type, value, timestamp)
            )
        
        # Persist transaction boundaries safely
        conn.commit()
        logger.info(f"Ingested and committed packet: {sensor_id} -> {value} at {timestamp}")
        
    except KeyError as key_error:
        logger.error(f"Ingestion payload rejected: Missing mandatory key element {key_error}")
    except json.JSONDecodeError:
        logger.error("Ingestion payload rejected: Inbound byte data stream is corrupted or unparsable")
    except Exception as runtime_error:
        logger.error(f"Pipeline thread encountered unexpected operational fault: {runtime_error}")
    finally:
        # Safely close the active database connection descriptor if it was allocated
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    # Initialize the core standalone engine instance for message routing
    client = mqtt.Client()
    client.on_message = on_message
    
    logger.info(f"Establishing runtime channel to message broker target: {BROKER}:{PORT}...")
    client.connect(BROKER, PORT)

    # Bind active listeners to each data stream topic configured in settings
    for topic in TOPICS:
        client.subscribe(topic)
        logger.info(f"Successfully configured stream subscription context: {topic}")

    logger.info("Collector ingestion layer fully active. Polling message streams...")
    # Enter blocking worker runtime context to fetch events indefinitely
    client.loop_forever()