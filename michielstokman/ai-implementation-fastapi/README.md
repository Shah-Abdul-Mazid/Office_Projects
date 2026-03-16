# Transform to Liberation — FastAPI AI Implementation

This is a Python/FastAPI implementation of the AI pipeline for MVP:

- `/generate` for single content generation (story/meditation)
- `/batch` for monthly batch generation
- Moderation gate for generated text
- TTS orchestration stub (mock + ElevenLabs-ready contract)
- OpenAI provider with mock fallback

## Run

```bash
pip install -r michielstokman/ai-implementation-fastapi/requirements.txt
uvicorn app.main:app --app-dir michielstokman/ai-implementation-fastapi --reload
```

## Environment Variables

- `USE_MOCK_AI=true` (default)
- `OPENAI_API_KEY=`
- `AI_MODEL=gpt-4.1-mini`
- `ELEVENLABS_API_KEY=`
- `MIN_WORDS=900`
- `MAX_WORDS=1500`
- `OUTPUT_DIR=./michielstokman/ai-implementation-fastapi/output`

## Example API calls

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"type":"story","title":"The Morning I Chose Space","growth_area":"Fear & Freedom","life_phase":"Recalibrating","voice":"Guide"}'
```

```bash
curl -X POST http://127.0.0.1:8000/batch \
  -H "Content-Type: application/json" \
  -d '{"month":"2026-03","items":[{"type":"story","title":"The Morning I Chose Space","growth_area":"Fear & Freedom","life_phase":"Recalibrating","voice":"Guide"},{"type":"meditation","title":"Breath Before the Next Step","growth_area":"Love & Connection","life_phase":"Deepening","minutes":7,"voice":"Student"}]}'
```
