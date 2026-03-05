# ARMA IoT Platform

IoT device management, data collection, and monitoring platform.

## Architecture

| Service | Description | Port |
|---------|-------------|------|
| Auth Server | Authentication & authorization | 9301 |
| Device Manager | IoT device lifecycle | - |
| Data Manager | Telemetry processing | - |
| Identity | User identity | - |
| Administration | System admin | - |
| Language | Localization | - |
| Tomcat | Legacy web app | 8080 |

## Infrastructure Dependencies

- **Database**: TimescaleDB (PostgreSQL)
- **Cache**: Redis (db:0)
- **Message Queue**: RabbitMQ, Apache Kafka
