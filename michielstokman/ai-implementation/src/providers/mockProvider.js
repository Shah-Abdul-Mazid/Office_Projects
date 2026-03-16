async function generateJsonFromPrompt(prompt) {
  const isMeditation = prompt.toLowerCase().includes("guided meditation");
  const type = isMeditation ? "meditation" : "story";
  return {
    title: isMeditation ? "A Gentle Return" : "The Door I Finally Opened",
    type,
    language: "en",
    growthArea: "Fear & Freedom",
    lifePhase: "Recalibrating",
    content: isMeditation
      ? "Close your eyes if that feels safe... Breathe slowly..."
      : "I used to think freedom had to be loud. Then one quiet morning...",
  };
}

module.exports = { generateJsonFromPrompt };
