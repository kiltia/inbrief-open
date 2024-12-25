# Scraper (API may be changed)

This module is responsible for information retrieval — text data, embeddings,
social features, etc.

## Configuration

### Telegram API

To work with it you need to create Telegram application, add `session_path`, `api_id` and `api_hash` fields in .env file and place it to `config` folder.

### OpenAI API

If you want to use embeddings from OpenAI API, you also need to pass
`openai_api_key` from paid account in `<project-root>/config/settings.json`.

### Database

This service uses PostgreSQL, 
which is being configured from `<project-root>/config/settings.json` file.


## Running

This application is built using FastAPI, so you may use
```
uvicorn --app-dir=src main:app
```
command.

NOTE: running this outside of container requires changing corresponding host
and port in Supervisor service configuration.

But since this service is a part of inbrief project, you may use `docker-compose up/docker-compose start scraper`
in any child directory. 

NOTE: As this service depends on `openai-api` repo, private ssh key is required
to build image. You'll need to place `.id_ed25519` in `scraper` directory with
access to our `openai_api` repository.

## API

Port: 6003 -> 8000

### POST /scraper/
- `channels (array)` — list of channels
- `required_embedders` (default: all available) — list of required embedders
- `offset_date (datetime)` (default: last message) — the most recent message date
- `end_date (datetime)`, (default: first message) — the oldest message date
- `social` (default: false) — comments, reactions
- `markup` (default: false) — Post classification using OpenAI API
- `classify_model` (default: gpt-3.5-turbo, used: `markup` is true) — Name of OpenAI model
- `max_retries` (default: 1, used: `markup is true`) — Maximum OpenAI prompt attempts per request

Example request:
```
{
  "channels": [
    "string"
  ],
  "required_embedders": [
    "string"
  ],
  "offset_date": "string",
  "end_date": "01/01/01 00:00:00",
  "social": false,
  "markup": false,
  "classify_model": "gpt-3.5-turbo",
  "max_retries": 1
}
```
