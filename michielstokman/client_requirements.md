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








