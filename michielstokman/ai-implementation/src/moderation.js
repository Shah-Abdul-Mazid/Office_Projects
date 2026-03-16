const blockedPatterns = [
  /self-harm/i,
  /suicide/i,
  /medical advice/i,
  /hate speech/i,
];

function moderateContent(text) {
  const issues = blockedPatterns.filter((rx) => rx.test(text)).map((rx) => rx.toString());
  return {
    approved: issues.length === 0,
    issues,
  };
}

module.exports = { moderateContent };
