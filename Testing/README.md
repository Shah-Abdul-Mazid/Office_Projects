# AI Storytelling Platform

FastAPI service for generating dual-role AI storytelling episodes, rendering them to speech, publishing podcast-ready RSS, and notifying downstream automation via webhook.

## Features

- `POST /episodes/generate` creates an episode, generates a Guide/Student script with OpenAI, and starts background audio rendering.
- `GET /episodes/{id}` returns episode status and the final audio URL once rendering finishes.
- `GET /rss/podcast.xml` exposes a podcast-ready RSS 2.0 feed for completed episodes.
- Supports local file serving or S3-compatible object storage for final MP3 delivery.
- Sends a webhook notification to tools such as n8n when an episode finishes.

## Project layout

```text
app/
  api/routes/
  core/
  db/
  models/
  schemas/
  services/
storage/
  audio/
  chunks/
```

## Setup

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and provide your PostgreSQL connection, OpenAI API key, and optional storage/webhook settings.

3. Ensure `ffmpeg` is installed and available on `PATH`. `pydub` relies on it for MP3 concatenation/export.

4. Run the API:

```bash
uvicorn app.main:app --reload
```

## Notes

- The app uses `FastAPI BackgroundTasks` for the audio pipeline, so generation starts immediately after the script is stored.
- Database tables are created on startup for convenience. For production, introduce Alembic migrations.
- Local audio files are served from `/media/audio/*`.
