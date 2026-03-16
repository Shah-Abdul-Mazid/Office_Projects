const { config } = require("./config");

async function synthesizeAudio({ text, voice = "Guide", itemId }) {
  if (!text) throw new Error("Missing text for TTS");

  if (!config.elevenLabsApiKey) {
    return {
      status: "mock_ready",
      provider: "mock",
      voice,
      audioUrl: `https://audio.local/${itemId || "item"}-${voice}.mp3`,
      note: "ELEVENLABS_API_KEY not set; returned mock URL",
    };
  }

  return {
    status: "queued",
    provider: "elevenlabs",
    voice,
    audioUrl: null,
    note: "Implement provider-specific TTS POST and storage upload in production environment",
  };
}

module.exports = { synthesizeAudio };
