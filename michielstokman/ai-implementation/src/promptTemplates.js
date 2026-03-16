function storyPrompt({ title, growthArea, lifePhase, minWords, maxWords }) {
  return `You are writing for Transform to Liberation.
Write a first-person emotional story titled "${title}".
Constraints:
- Word count: ${minWords}-${maxWords}
- Growth area focus: ${growthArea}
- Life phase: ${lifePhase}
- Tone: grounded, humane, emotionally safe, hopeful
- Include one subtle liberation turning point
- Avoid clichés and unsafe claims
Output JSON with keys: title, type, language, growthArea, lifePhase, content`;
}

function meditationPrompt({ title, growthArea, lifePhase, minutes = 7 }) {
  return `You are writing for Transform to Liberation.
Write a second-person guided meditation script titled "${title}".
Constraints:
- Length target: ${minutes} minutes spoken pace
- Growth area focus: ${growthArea}
- Life phase: ${lifePhase}
- Include breath guidance, body awareness, and gentle closing
- Tone: calm, non-judgmental, consent-oriented
Output JSON with keys: title, type, language, growthArea, lifePhase, content`;
}

module.exports = { storyPrompt, meditationPrompt };
