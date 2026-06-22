# =================================================================
#  Edge IoT Sensor Simulator - LSS Project
#  This script simulates local sensor readings (telemetry) and
#  publishes them as standardized JSON packets over MQTT.
# =================================================================

import paho.mqtt.client as mqtt
import random
import time
import json
import os
import logging
from datetime import datetime, timezone

# Establish standard structured output logging for telemetry metrics tracing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fetch application environment configs dynamically injected by Docker Compose
BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", 1883))

def get_sensor_data():
    """
    Generates a localized batch snapshot of synchronized edge readings,
    stamping data with precise UTC context directly from the host system.
    """
    # Create high-precision localized timestamp at the exact moment of sampling
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Pack values mimicking realistic hardware sensor behavior bounds
    return [
        {
            "sensor_id": "sensor_temperature_1",
            "sensor_type": "temperature",
            "value": round(random.uniform(15.0, 40.0), 2),
            "timestamp": current_time
        },
        {
            "sensor_id": "sensor_humidity_1",
            "sensor_type": "humidity",
            "value": round(random.uniform(20.0, 90.0), 2),
            "timestamp": current_time
        },
        {
            "sensor_id": "sensor_air_quality_1",
            "sensor_type": "air_quality",
            "value": round(random.uniform(0.0, 500.0), 2),
            "timestamp": current_time
        }
    ]

if __name__ == "__main__":
    # Initialize the core standalone network client interface instance
    client = mqtt.Client()
    
    logger.info(f"Establishing runtime channel to message broker target: {BROKER}:{PORT}...")
    # Enforce standard thread delay buffer to avoid container race collisions
    time.sleep(2)
    client.connect(BROKER, PORT)

    logger.info("Simulation matrix active. Initializing data loop routine...")

    while True:
        try:
            # Map metrics data array structure out to active network topic channels
            for sensor in get_sensor_data():
                topic = f"sensors/{sensor['sensor_type']}"
                payload = json.dumps(sensor)
                
                # Push processed JSON text representation data packets over the wire
                client.publish(topic, payload)
                logger.info(f"Dispatched frame -> [{topic}]: {payload}")
            
            # Enforce data rate compliance window (5 seconds data capture delta)
            time.sleep(5)
        except Exception as loop_error:
            logger.error(f"Broadcast thread execution caught networking exception: {loop_error}")
            # Cool down thread loop to protect edge processing availability stability
            time.sleep(5)