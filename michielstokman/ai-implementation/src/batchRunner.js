const fs = require("fs/promises");
const path = require("path");
const crypto = require("crypto");
const { config } = require("./config");
const { generateContent } = require("./storyGenerator");
const { synthesizeAudio } = require("./ttsOrchestrator");

function id() {
  return crypto.randomBytes(6).toString("hex");
}

async function runBatch(batchSpec) {
  const results = [];

  for (const item of batchSpec.items) {
    const itemId = id();
    try {
      const generated = await generateContent(item);
      const tts = await synthesizeAudio({ text: generated.content, voice: item.voice || "Guide", itemId });

      results.push({
        id: itemId,
        input: item,
        generated,
        tts,
        status: generated.moderation.approved ? "ready_for_review" : "blocked_by_moderation",
      });
    } catch (error) {
      results.push({
        id: itemId,
        input: item,
        status: "failed",
        error: String(error.message || error),
      });
    }
  }

  await fs.mkdir(config.outputDir, { recursive: true });
  const outFile = path.join(config.outputDir, `batch-${Date.now()}.json`);
  await fs.writeFile(outFile, JSON.stringify({ batchSpec, results }, null, 2), "utf8");

  return { outFile, results };
}

module.exports = { runBatch };
