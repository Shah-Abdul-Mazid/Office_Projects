# 🧘 AI Story & Meditation Studio (Backend)

A powerful, standalone AI-powered storytelling and meditation platform built with **FastAPI**. This system automatically generates deep, long-form meditation scripts, converts them into high-quality multi-voice narration for free, and prepares them for podcast and social media distribution.

---

## 🚀 Key Features

*   **AI Story Generation**: Craft 900–1500 word meditation scripts via OpenAI GPT-4o-mini.
*   **Free Multi-Voice TTS**: High-quality 'Guide' and 'Student' voices using `edge-tts` (No API keys required for audio).
*   **Bulk Month Generation**: Background processing for generating 30+ episodes in one click.
*   **Spotify-Ready RSS**: Automated `rss_feed.xml` with full iTunes/Spotify metadata compatibility.
*   **Social Media Automation**: Automated platform-specific copy generation for Facebook & Instagram (Meta Graph API).
*   **Integrated Library**: Secure SQLite database and file management for all audio assets.

---

## 🛠️ Getting Started

### 1. Prerequisites
*   Python 3.10+
*   OpenAI API Key

### 2. Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration (`.env`)
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_key
PUBLIC_BASE_URL=http://localhost:8000
DATABASE_URL=sqlite:///./studio.db
SECRET_KEY=generate_a_secure_key
```

### 4. Running the Server
```bash
uvicorn app.main:app --reload
```
Once running, visit **`http://localhost:8000/docs`** for the interactive API documentation.

---

## 🎧 API Usage Flow

1.  **Login**: Authenticate via `POST /token` (Default: `admin@example.com` / `admin123`).
2.  **Generate**: Use `POST /stories/full` for a complete script + voiceover.
3.  **Listen**: Access audio via `http://localhost:8000/audio/guide.mp3`.
4.  **Publish**: Point your podcast host (Spotify/Buzzsprout) to `http://your-ip:8000/rss_feed.xml`.

---

## 📂 Project Structure
*   `app/main.py`: API endpoints and core logic.
*   `app/services/ai_story.py`: OpenAI generation pipeline.
*   `app/services/tts.py`: Free Edge-TTS integration.
*   `app/services/orchestrator.py`: Full automation system (RSS + Social).
*   `output/library/`: Storage for all generated episodes and assets.
