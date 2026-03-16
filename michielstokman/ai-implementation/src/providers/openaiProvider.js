const { config } = require("../config");

async function generateJsonFromPrompt(prompt) {
  if (!config.openAiApiKey) {
    throw new Error("OPENAI_API_KEY is required when USE_MOCK_AI=false");
  }

  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${config.openAiApiKey}`,
    },
    body: JSON.stringify({
      model: config.model,
      temperature: 0.7,
      messages: [
        { role: "system", content: "Return valid JSON only." },
        { role: "user", content: prompt },
      ],
    }),
  });

  if (!res.ok) {
    throw new Error(`OpenAI request failed: ${res.status} ${await res.text()}`);
  }

  const data = await res.json();
  const text = data?.choices?.[0]?.message?.content || "{}";

  try {
    return JSON.parse(text);
  } catch {
    const start = text.indexOf("{");
    const end = text.lastIndexOf("}");
    if (start >= 0 && end > start) {
      return JSON.parse(text.slice(start, end + 1));
    }
    throw new Error("Model response was not valid JSON");
  }
}

module.exports = { generateJsonFromPrompt };
