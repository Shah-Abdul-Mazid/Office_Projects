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
