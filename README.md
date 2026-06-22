# [IoT Environmental Monitoring System]
## Infrastructure Orchestration & Real-Time Data Pipeline

This project provides a production-grade, fully containerized implementation of an **IoT Environmental Monitoring System**. By deploying a highly resilient microservice architecture, the system orchestrates simulated edge devices, a central Message Queuing Telemetry Transport (MQTT) broker, a backend ingestion pipeline, a relational time-series storage schema, and an automated visualization frontend.

The core objective of this infrastructure is to demonstrate advanced concepts in **Systems Architecture**, including publish-subscribe (Pub/Sub) routing topology, cross-container startup synchronization (race-condition mitigation), secure dynamic configuration via multi-environment injection, network isolation, and declarative provisioning.

---

## 1. System Architecture & Lifecycle

The platform is engineered using five decoupled, specialized services that communicate within an isolated virtual bridge network layer.

```
[ Edge Sensors ] ---> ( MQTT Topic: sensors/* ) ---> [ Mosquitto Broker ]
                                                              |
                                                     (Inbound Stream)
                                                              v
[ PostgreSQL ]  <--- ( Persisted SQL ) <----------- [ Data Collector ]
      |
(Auto-Provisioned)
      v
[ Grafana Dashboard (UI) ]
```

### 1.1 Components Walkthrough

1. **Edge Telemetry Simulation (`sensors`):** A standalone Python engine mimicking a multi-sensor hardware deployment. It encapsulates internal sampling loop routines that build structured, standardized JSON text array data blocks, executing atomic sensor-side timestamping to enforce strict mathematical clock synchronization.
2. **Message Broker (`mosquitto`):** An Eclipse Mosquitto instance acting as the stateless routing backbone. It exposes an unencrypted local socket listener tailored for high-throughput, low-overhead binary frame dispatching.
3. **Data Collector Service (`collector`):** A high-resilience Python background daemon. It binds a concurrent network client thread to the broker, intercepts inbound stream payloads, applies unmarshalling validation, and executes transactional persistence operations safely via automatic cursor lifecycle managers.
4. **Relational Database (`database`):** A PostgreSQL 15 database engine tuned for tabular historical data tracking. It consumes specialized data definition language (DDL) initialization files to structure catalog tables upon its initial volume boot.
5. **Analytics Frontend (`grafana`):** An automated Grafana instance serving as the operational control panel. It uses native provisioning file matrices to auto-configure data source connections and load optimized analytical layout panels without manual user intervention.

### 1.2 Core Architectural Methodologies

* **Sensor-Side Timestamping vs Broker-Side:** To ensure physical truth in data logging, timestamps are captured at the exact millisecond of sampling inside the edge node using explicit UTC formats. This architecture guarantees data timeline integrity if network delivery latency occurs between the edge and the broker.
* **Network Segregation & Isolation:** The MQTT broker (`mosquitto`) has been stripped of public port exposure to the host machine. It is locked inside the internal virtual container bridge network (`iot_network`). This prevents unauthorized external clients from injecting malicious telemetry frames, enforcing strict backend-to-backend communication boundaries.

---

## 2. Directory Structure Matrix

```
.
├── collector/                              # Backend Ingestion Layer Microservice
│   ├── collector.py                        # High-resilience Python ingestion worker daemon
│   ├── Dockerfile                          # Multi-stage lightweight python runtime build file
│   └── requirements.txt                    # Explicit third-party database and networking library handles
├── database/                               # Relational Engine Data Definitions
│   └── init.sql                            # DDL schema footprint catalog initialization script
├── grafana/                                # UI Frontend Automated Provisioning
│   └── provisioning/                       # Declarative automation manifests
│       ├── dashboards/                     # Folder scanning path for dashboard templates
│       │   ├── dashboard.json              # Complete graphical panel layout and metric SQL query matrix
│       │   └── dashboard_provider.yml      # Automated layout provisioning paths manifest
│       └── datasources/                    # Automated engine connectivity handles
│           └── datasource.yml              # Dynamic PostgreSQL credentials and proxy mapping file
├── mosquitto/                              # In-Transit Message Routing Core
│   └── mosquitto.conf                      # Network binding, anonymous authorization, and log matrices
├── sensors/                                # Edge Device Telemetry Simulator Microservice
│   ├── sensor.py                           # Loop routine simulating physical sensor matrix sampling
│   ├── Dockerfile                          # Optimized scratch-to-build Python slim container file
│   └── requirements.txt                    # Isolated lightweight dependency file mapping (paho-mqtt)
├── .env                                    # Centralized, hidden environmental configurations matrix
├── .gitignore                              # Declares untracked system patterns and credentials file paths
├── docker-compose.yml                      # Central infrastructure multi-container orchestration matrix
└── README.md                               # Comprehensive system engineering specification manual
```

---

## 3. Configuration & Environmental Variables

The configuration layout follows the modern **12-Factor App methodology**, separating infrastructure code from operational state variables. All sensitive variables, system credentials, and target networking boundaries are isolated inside a centralized `.env` file located at the root of the project.

### 3.1 The `.env` Configuration File Blueprint

Create a file named `.env` in the root directory and define the following schema variables:

```ini
# =================================================================
#  Global System Environment Manifest - LSS Project Credentials
# =================================================================

# Database Storage Engine Parameters
DB_HOST=database
DB_PORT=5432
DB_NAME=iot_db
DB_USER=iot_user
DB_PASSWORD=production_secure_pass_2026

# In-Transit Message Broker Parameters
MQTT_BROKER=mosquitto
MQTT_PORT=1883
```

### 3.2 Security and Production Advantages

* **Decoupled Architecture:** Modifying a database credential or switching a network target port does not require rewriting Python code or rebuilding Docker images. The orchestration engine dynamically injects these properties at runtime.
* **Credential Safety:** The `.env` file is explicitly blocked inside `.gitignore`. This ensures system passwords are never leaked into public version control repositories (GitHub), fulfilling strict corporate compliance rules.

---

## 4. Resilience and Fault Tolerance Analysis

A critical challenge in microservice topologies is the **initialization race condition**: when a multi-container network boots simultaneously, backend services usually start faster than the database can spin up its low-level TCP listening sockets. This project solves that structural vulnerability through two layers of resilience.

### 4.1 Orchestration Layer Healthchecks

Docker Compose uses declarative state synchronization parameters via native system healthcheck routines:

* **The Broker Healthcheck:** Executes a localized un-subscription test loop checking if mosquitto is ready to route packets.
* **The Database Healthcheck:** Spins up internal standard commands (`pg_isready`) inside the database container.
* **Downstream Blockers:** The `collector` and `sensors` microservices use explicit `condition: service_healthy` configurations. They are completely locked at boot phase, waiting until the upstream dependencies pass their health evaluations.

### 4.2 Application Layer Retry and Lifecycle Safety

If transient network fluctuations happen during runtime, the code utilizes custom fallback blocks:

* **The `get_db_connection()` Retry Loop:** Built with a backoff delay, the collector thread will intercept connectivity drops (`OperationalError`), catch the failure safely without causing a fatal crash, log a warning, and sleep for 5 seconds across 5 sequential recovery attempts before aborting execution.
* **Context Manager Pointer Isolation:** Inside `on_message()`, the database cursor lifecycle is wrapped inside a secure Python context manager (`with conn.cursor() as cursor:`). This pattern guarantees that regardless of processing runtime anomalies or broken SQL packets, data descriptor streams are strictly and automatically closed, avoiding server-side memory leaks (resource exhaustion).
* **The `finally` Cleanup Block:** Global connections are wrapped inside a definitive `try/except/finally` structural pattern. The database socket connection descriptor handle is evaluated at the end of the execution thread; if it remains active, it is explicitly closed (`conn.close()`), keeping the application robust under continuous runtime pressure.

---

## 5. Deployment and Verification Guide

### 5.1 Prerequisites

Ensure your local host machine has the following packages installed:

* Docker Engine (v20.10.0 or higher)
* Docker Compose V2 (Integrated tool bundle)

### 5.2 Booting the System

To compile the local Python images, provision the database tables, link the automated dashboards, and execute the runtime network stack, run the following command from the root folder:

```bash
docker compose up --build -d
```

Flags used: `--build` forces compilation of the localized Dockerfiles; `-d` launches the stack in detached background mode, freeing up your active shell session.

### 5.3 Validating Microservice Health and Operations

To monitor the telemetry ingestion process and inspect live system state logs, run:

```bash
docker compose logs -f --tail=20
```

Expected System Verification Pattern:

```
mosquitto    | 1719234510: New client connected from 172.20.0.4:51234 as auto-A1 (p1, c1, k60).
sensors      | 2026-06-22 22:54:12,102 - INFO - Dispatched frame -> [sensors/temperature]: {"sensor_id": "sensor_temperature_1", "sensor_type": "temperature", "value": 24.52, "timestamp": "2026-06-22T21:54:12.101Z"}
collector    | 2026-06-22 22:54:12,156 - INFO - Ingested and committed packet: sensor_temperature_1 -> 24.52 at 2026-06-22T21:54:12.101Z
```

### 5.4 Accessing the Analytics Interface

Once the microservices are fully operational:

1. Open your browser and navigate to: **http://localhost:3000**
2. The user account configuration is bypassed or pre-authenticated depending on your environmental rules.
3. Access the Dashboard folder: **IoT Environmental System → IoT Environment Control Panel**.
4. You will find a real-time tracking interface featuring a unified Time-Series layout chart and three statistical monitoring widgets rendering live data points updated dynamically every 5 seconds.

---

## 6. System Cleanup and State Reset

To gracefully spin down the container stack, release allocated host network socket bindings, and preserve data integrity, use the standard teardown routine:

```bash
docker compose down
```

If you wish to perform a complete system reset — completely purging the persistent database storage volumes to replicate a clean, scratch-to-build deployment:

```bash
docker compose down -v
```

> **Warning:** The `-v` flag deletes the `db_data` volume block, erasing all historical logged data records.

## Authors

[Iury Figueredo](https://github.com/IuryFigueredo) (N. 132655)

[Guilherme Maia](https://github.com/guilhermemaiaUA) (N. 117596)
