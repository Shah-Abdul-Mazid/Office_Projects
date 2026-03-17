# AI Storytelling Platform Backend

Production-oriented FastAPI scaffold for generating meditation and storytelling scripts,
rendering multi-voice narration, and tracking asynchronous processing state.

## Folder structure

```text
.
|- alembic/
|- app/
|  |- api/v1/endpoints/
|  |- core/
|  |- db/
|  |- models/
|  |- schemas/
|  |- services/
|  |- workers/tasks/
|- .env.example
|- alembic.ini
|- pyproject.toml
```

## Core flow

1. `POST /api/v1/scripts/generations` stores the generation request and creates a
   `script_generation` job.
2. Celery runs the OpenAI generation task and persists structured dialogue segments for
   `GUIDE` and `STUDENT`.
3. The TTS task renders each segment with the correct voice, uploads assets to S3, and stores
   audio metadata.
4. Clients poll script, job, and audio endpoints until the script reaches `ready`.
