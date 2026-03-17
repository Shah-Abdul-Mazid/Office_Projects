# AI Story & Meditation Studio

A FastAPI backend that uses OpenAI to draft 900–1500-word story/meditation episodes and renders them into Guide + Student voice tracks for narration.

## Core Features
- AI-generated episodes with semantic sections (Introduction, Journey, Reflection, Close) plus optional focus/pacing hints.
- Multi-voice TTS with separate Guide and Student cues backed by gtts.
- Downloadable narration files served from output/audio/ for cataloging and reuse.
- Monthly bulk story generation hook via POST /stories/full to seed a content library.
- Audio management system that keeps every Guide/Student track and attaches UUID-named MP3s to the library pipeline.
- Automated daily RSS publishing workflow that pushes the latest episodes (Guide + Student audio) to Spotify, Apple Podcasts, and other audio platforms.
- Social media automation hooks so the same episode text drives Facebook and Instagram captions along with creative prompts.
- Feedback capture connectors that log user interactions (likes, skips, ratings) so you can refine prompt templates and pacing.
- Multi-language readiness: swap theme/mood prompts per locale, translate audience cues, and map oice_tld_overrides to regional Google TLDs so stories and promotional posts sound native.

## Operations & Automation
- **Daily RSS publishing** – schedule a job that calls /orchestrate, saves the returned MP3s, and mines the RSS feed (ss_feed.xml) for every release.
- **Social media automation** – reuse the generated 	itle/episode_text summary to emit Facebook and Instagram posts (the response includes social_copy you can pipe into your marketing stack).
- **Feedback capture** – each orchestration run appends a row to eedback_log.csv, letting you measure audience response and adjust future prompts.
- **Multi-language content** – orchestrate localized episodes by changing the prompt inputs and updating oice_tld_overrides so both stories and promotions stay culturally in tune.

## Setup
1. Create and activate a virtual environment (e.g., python -m venv .venv followed by .\\venv\\Scripts\\Activate on Windows).
2. Install dependencies: pip install -r requirements.txt.
3. Copy .env.example to .env and set OPENAI_API_KEY plus any other overrides (RSS path, feedback path).
4. Start the server: uvicorn app.main:app --reload (omit --reload on Windows if the reload pipe fails).

## Endpoints
- POST /stories: Submit 	heme, udience, mood, and optional ocus/pacing. Returns the generated episode text, word count, used model, and placeholder voice markers.
- POST /stories/full: Create the episode, clean the Markdown-heavy script, and synthesize Guide/Student narration in one go. The response includes guidance_audio paths for both voices so you never paste the text manually.
- POST /orchestrate: Run the full studio workflow—story generation, Guide + Student TTS, RSS feed update, feedback logging, and social copy output—in a single request.
- POST /stories/tts: Provide story text plus voice (guide or student) to produce a narrated MP3 path.
- GET /audio/{file_name}: Download a previously saved voice track.

## Voice Guidance
Guide and Student voices map to different Google TLDs to keep their timbre distinct. Each TTS call saves a UUID-named MP3 in output/audio/, so you can regenerate either voice without overwriting earlier files.

## Notes
- Keep the OpenAI API key outside version control and refresh it if you see a Quota exceeded or billing warning on [Platform OpenAI](https://platform.openai.com).
- Adjust MIN_STORY_WORDS/MAX_STORY_WORDS in .env if you need longer or shorter episodes for certain channels.
