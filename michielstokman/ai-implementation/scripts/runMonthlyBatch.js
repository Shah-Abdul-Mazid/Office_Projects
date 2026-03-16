#!/usr/bin/env node
const { runBatch } = require("../src/batchRunner");

const sampleBatch = {
  month: "2026-03",
  items: [
    {
      type: "story",
      title: "The Morning I Chose Space",
      growthArea: "Fear & Freedom",
      lifePhase: "Recalibrating",
      voice: "Guide",
    },
    {
      type: "meditation",
      title: "Breath Before the Next Step",
      growthArea: "Love & Connection",
      lifePhase: "Deepening",
      minutes: 7,
      voice: "Student",
    },
  ],
};

(async () => {
  const { outFile, results } = await runBatch(sampleBatch);
  console.log(`Batch complete. Output: ${outFile}`);
  console.log(`Items processed: ${results.length}`);
  console.log(`Ready for review: ${results.filter((x) => x.status === "ready_for_review").length}`);
  console.log(`Blocked: ${results.filter((x) => x.status === "blocked_by_moderation").length}`);
  console.log(`Failed: ${results.filter((x) => x.status === "failed").length}`);
})();
