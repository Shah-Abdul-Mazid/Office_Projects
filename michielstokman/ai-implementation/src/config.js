const config = {
  model: process.env.AI_MODEL || "gpt-4.1-mini",
  openAiApiKey: process.env.OPENAI_API_KEY || "",
  elevenLabsApiKey: process.env.ELEVENLABS_API_KEY || "",
  useMock: (process.env.USE_MOCK_AI || "true").toLowerCase() === "true",
  outputDir: process.env.OUTPUT_DIR || "./michielstokman/ai-implementation/output",
  generation: {
    minWords: Number(process.env.MIN_WORDS || 900),
    maxWords: Number(process.env.MAX_WORDS || 1500),
  },
};

module.exports = { config };
