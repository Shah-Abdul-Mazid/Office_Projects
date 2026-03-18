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






# 🧘 AI Story & Meditation Studio: Client Setup Guide

This guide contains everything needed to set up, configure, and distribute the AI Story & Meditation Studio.

---

## 📋 Part 1: Client Requirements Checklist
*To be provided by the client for full deployment.*

### 1. AI & Core Services (API Keys)
*   [ ] **OpenAI API Key**: Required for the AI story generation (GPT-4o / GPT-4o-mini).
*   [ ] **ElevenLabs API Key** *(Optional)*: Only needed if the client prefers premium ElevenLabs voices over the current free Edge-TTS implementation.
*   [ ] **Twelve Labs / Other** *(Optional)*: If future video generation is required.

### 2. Distribution & Publishing (Platform Access)
*   [ ] **Podcast Hosting Access**: Credentials for **Buzzsprout**, **Castopod**, or similar to host the audio files and RSS feed.
*   [ ] **Spotify for Podcasters**: Access to submit the RSS feed specifically to Spotify.
*   [ ] **Apple Podcasts / Amazon Music**: Credentials if listing on these platforms is required.

### 3. Social Media Automation (API Access)
*   [ ] **Meta Developer Account**: Access to create an App in the [Meta for Developers](https://developers.facebook.com/) portal.
*   [ ] **Facebook Page ID & Token**: Admin access to the specific Facebook Page where stories will be posted.
*   [ ] **Instagram Professional Account**: The Instagram account must be linked to the Facebook page to use the Meta Graph API.

### 4. Technical Environment
*   [ ] **Server / VPS Access**: Access to the hosting environment (e.g., AWS, DigitalOcean, Heroku).
*   [ ] **Domain Name / Public IP**: A fixed public address to configure the `PUBLIC_BASE_URL`.
*   [ ] **SMTP Credentials**: If the system needs to send automated emails.

### 5. Content Branding
*   [ ] **Podcaster Name/Author**: To be displayed in the RSS feed.
*   [ ] **Podcast Logo/Thumbnail**: 3000x3000px image required by Spotify/Apple.
*   [ ] **Language Requirements**: List of specific languages the AI should prioritize.

---

## 🔑 Part 2: API Key & Configuration Guide
*Technical details for setting up the `.env` file.*

### 1. AI Generation (Required)

| Key | Purpose | Source |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | Generates meditation scripts & titles. | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `OPENAI_MODEL` | Defaults to `gpt-4o-mini` for cost efficiency. | - |

### 2. Text-to-Speech (TTS)
*The system currently uses **Edge-TTS**, which is **FREE** and requires NO API keys.*

| Key | Purpose | Source |
| :--- | :--- | :--- |
| `EDGE_TTS_GUIDE_VOICE` | Default: `en-US-GuyNeural` | [Edge TTS Voice List](https://gist.github.com/Gisheh/168e36780824b2f2933f81e695f36e89) |
| `EDGE_TTS_STUDENT_VOICE`| Default: `en-US-AvaNeural` | - |

### 3. Social Media Automation (Phase 3)

| Key | Purpose | Source |
| :--- | :--- | :--- |
| `META_FACEBOOK_TOKEN` | Permanent Page Access Token. | [Meta for Developers](https://developers.facebook.com/) |
| `FB_PAGE_ID` | The ID of your Facebook Page. | Page Settings > About |
| `IG_USER_ID` | The ID of your Instagram Business Account. | Linked via Facebook Page |

### 4. Security & Database

| Key | Purpose | Source |
| :--- | :--- | :--- |
| `SECRET_KEY` | Used to sign JWT tokens. | Create a long random string. |
| `PUBLIC_BASE_URL` | Your server's public address. | e.g. `http://1.2.3.4:8000` |

---

## 🔧 Pro Tip: Setting up `.env`
Create a file named `.env` in the root folder and paste your keys like this:
```env
OPENAI_API_KEY=sk-xxxx...
META_FACEBOOK_TOKEN=EAAB...
SECRET_KEY=yoursecretphrase
PUBLIC_BASE_URL=http://your-server-address
```






# 📋 Client Requirements Checklist

To fully develop and deploy the **AI Story & Meditation Studio**, you will need the following information and access from your client.

## 1. AI & Core Services (API Keys)
*   [ ] **OpenAI API Key**: Required for the AI story generation (GPT-4o / GPT-4o-mini).
*   [ ] **ElevenLabs API Key** *(Optional)*: Only needed if the client prefers premium ElevenLabs voices over the current free Edge-TTS implementation.
*   [ ] **Twelve Labs / Other** *(Optional)*: If future video generation is required.

## 2. Distribution & Publishing (Platform Access)
*   [ ] **Podcast Hosting Access**: Credentials for **Buzzsprout**, **Castopod**, or similar to host the audio files and RSS feed.
*   [ ] **Spotify for Podcasters**: Access to submit the RSS feed specifically to Spotify.
*   [ ] **Apple Podcasts / Amazon Music**: Credentials if listing on these platforms is required.

## 3. Social Media Automation (API Access)
*   [ ] **Meta Developer Account**: Access to create an App in the [Meta for Developers](https://developers.facebook.com/) portal.
*   [ ] **Facebook Page ID & Token**: Admin access to the specific Facebook Page where stories will be posted.
*   [ ] **Instagram Professional Account**: The Instagram account must be linked to the Facebook page to use the Meta Graph API.

## 4. Technical Environment
*   [ ] **Server / VPS Access**: Access to the hosting environment (e.g., AWS, DigitalOcean, Heroku) where the FastAPI backend will run.
*   [ ] **Domain Name / Public IP**: A fixed public address to configure the `PUBLIC_BASE_URL` (essential for Spotify to reach the audio files).
*   [ ] **SMTP Credentials**: If the system needs to send automated emails to the client or users.

## 5. Content Branding
*   [ ] **Podcaster Name/Author**: To be displayed in the RSS feed.
*   [ ] **Podcast Logo/Thumbnail**: 3000x3000px image required by Spotify/Apple.
*   [ ] **Language Requirements**: List of specific languages the AI should prioritize.







# 🔑 API Key & Configuration Guide

This document lists all the API keys and environment variables required to fully configure the **AI Story & Meditation Studio** backend.

## 1. AI Generation (Required)

| Key | Purpose | Source |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | Generates meditation scripts & titles. | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `OPENAI_MODEL` | Defaults to `gpt-4o-mini` for cost efficiency. | - |

## 2. Text-to-Speech (TTS)

> [!NOTE]
> The system currently uses **Edge-TTS**, which is **FREE** and requires NO API keys.

| Key | Purpose | Source |
| :--- | :--- | :--- |
| `EDGE_TTS_GUIDE_VOICE` | Default: `en-US-GuyNeural` | [Edge TTS Voice List](https://gist.github.com/Gisheh/168e36780824b2f2933f81e695f36e89) |
| `EDGE_TTS_STUDENT_VOICE`| Default: `en-US-AvaNeural` | - |
| `ELEVENLABS_API_KEY` | *(Optional)* If you switch back to ElevenLabs. | [ElevenLabs Dashboard](https://elevenlabs.io/api) |

## 3. Social Media Automation (Phase 3)

| Key | Purpose | Source |
| :--- | :--- | :--- |
| `META_FACEBOOK_TOKEN` | Permanent Page Access Token. | [Meta for Developers](https://developers.facebook.com/) |
| `META_INSTAGRAM_TOKEN` | Token for Instagram Content Publishing. | [Meta for Developers](https://developers.facebook.com/) |
| `FB_PAGE_ID` | The ID of your Facebook Page. | Page Settings > About |
| `IG_USER_ID` | The ID of your Instagram Business Account. | Linked via Facebook Page |

## 4. Security & Database

| Key | Purpose | Source |
| :--- | :--- | :--- |
| `SECRET_KEY` | Used to sign JWT tokens. | Create a long random string. |
| `ALGORITHM` | Default: `HS256` | - |
| `DATABASE_URL` | Default: `sqlite:///./studio.db` | - |
| `PUBLIC_BASE_URL` | Your server's public address. | e.g. `http://1.2.3.4:8000` |

---

## 🔧 Pro Tip: Setting up `.env`
Create a file named `.env` in the root folder and paste your keys like this:
```env
OPENAI_API_KEY=sk-xxxx...
META_FACEBOOK_TOKEN=EAAB...
SECRET_KEY=yoursecretphrase
PUBLIC_BASE_URL=http://your-server-address
```








