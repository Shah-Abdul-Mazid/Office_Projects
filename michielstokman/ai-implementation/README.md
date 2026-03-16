# Transform to Liberation — AI Part Implementation (MVP)

This module implements the **AI pipeline** for MVP:

- Story/meditation prompt generation
- LLM generation provider abstraction (OpenAI + mock)
- Basic moderation gate
- TTS orchestration stub (mock + ElevenLabs-ready contract)
- Monthly batch runner that outputs JSON artifacts for admin review

## Structure

- `src/config.js` — environment config
- `src/promptTemplates.js` — prompt constructors
- `src/providers/openaiProvider.js` — OpenAI chat-completions JSON generator
- `src/providers/mockProvider.js` — local mock for offline/dev
- `src/moderation.js` — basic policy checks
- `src/storyGenerator.js` — generation + moderation pipeline
- `src/ttsOrchestrator.js` — TTS orchestration contract
- `src/batchRunner.js` — batch job processor
- `scripts/runMonthlyBatch.js` — executable monthly batch example

## Run

```bash
node michielstokman/ai-implementation/scripts/runMonthlyBatch.js
```

By default this runs in mock mode (`USE_MOCK_AI=true`) so it works without API keys.

## Optional env vars

- `USE_MOCK_AI=false`
- `OPENAI_API_KEY=...`
- `AI_MODEL=gpt-4.1-mini`
- `ELEVENLABS_API_KEY=...`
- `MIN_WORDS=900`
- `MAX_WORDS=1500`
- `OUTPUT_DIR=./michielstokman/ai-implementation/output`

## Production integration notes

- Replace TTS queued response with actual ElevenLabs synthesis + upload to Supabase/R2.
- Replace regex moderation with OpenAI/Anthropic moderation API and escalation flags.
- Move batch scheduling into queue worker (BullMQ/Supabase cron).
- Persist outputs to DB tables (`content_items`, `audio_assets`, `moderation_events`) instead of JSON files.
