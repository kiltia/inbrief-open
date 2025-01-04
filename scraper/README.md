# Scraper

This module is responsible for information retrieval — text data, embeddings,
social features, etc from Telegram channels.

## Configuration

Almost everything is configure from environment variables. You can find example in `.env-example` file.

### Kafka

This service is intended to be used with Kafka, so you should configure `KAFKA_HOST` variable.

### Telegram API

#### Variables

* `TELEGRAM__API_KEY` — Telegram API key
* `TELEGRAM__API_HASH` — Telegram API hash

Telegram session can be created using `generate-session` recipe in Justfile or via `python3 src/generate_session.py`.

You will need Telegram account with access to channels you want to scrape.


### Database

#### Variables

* `DATABASE__DRIVER` — Database driver
* `DATABASE__HOST` — Database host
* `DATABASE__PORT` — Database port
* `DATABASE__URL` — Database URL
* `DATABASE__DB_NAME` — Database name
* `DATABASE__USERNAME` — Database user
* `DATABASE__PASSWORD` — Database password

### Exporters

Scraper is supposed to export data to various data stores.

Currently, preferred data format is JSON.

You should list all required exporters via `EXPORTERS__REQUIRED_EXPORTERS` variable.

Available exporters:

- [x] File exporter - saves data to `EXPORTERS__JSON__PATH` directory
- [x] Redis exporter - saves data to Redis-like client with host equal to `EXPORTERS__REDIS__HOST` and port equal to `EXPORTERS__REDIS__PORT`
- [ ] S3 bucket exporter - saves data to S3 bucket

### Other configuration

Here's some legacy configuration in shared/settings.json file. It should be removed in future.


## Running

This application is managed via UV and built using FastStream, so you may use
```
uv run -- faststream run --app-dir src main:app --host 0.0.0.0 --reload
```
command.
