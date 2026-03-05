# PQM — Power Quality Monitor

Power quality monitoring and analysis platform.

## Architecture

| Service | Description | Port |
|---------|-------------|------|
| Auth Server | Authentication & authorization | 9901 |
| Host | Backend services | - |
| UI | Web interface | 9911 |
| Blazor | Blazor web app | 9902 |

## Infrastructure Dependencies

- **Database**: TimescaleDB (ArmaPQM database)
- **Cache**: Redis (db:10)
