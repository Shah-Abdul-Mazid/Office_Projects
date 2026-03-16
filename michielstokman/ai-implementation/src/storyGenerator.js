const { config } = require("./config");
const { storyPrompt, meditationPrompt } = require("./promptTemplates");
const mockProvider = require("./providers/mockProvider");
const openAiProvider = require("./providers/openaiProvider");
const { moderateContent } = require("./moderation");

function getProvider() {
  return config.useMock ? mockProvider : openAiProvider;
}

async function generateContent(item) {
  const prompt = item.type === "meditation"
    ? meditationPrompt({ title: item.title, growthArea: item.growthArea, lifePhase: item.lifePhase, minutes: item.minutes || 7 })
    : storyPrompt({
        title: item.title,
        growthArea: item.growthArea,
        lifePhase: item.lifePhase,
        minWords: config.generation.minWords,
        maxWords: config.generation.maxWords,
      });

  const generated = await getProvider().generateJsonFromPrompt(prompt);
  const moderation = moderateContent(generated.content || "");

  return {
    ...generated,
    moderation,
    createdAt: new Date().toISOString(),
  };
}

module.exports = { generateContent };
