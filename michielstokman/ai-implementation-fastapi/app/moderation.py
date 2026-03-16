import re

BLOCKED_PATTERNS = [
    re.compile(r'self-harm', re.I),
    re.compile(r'suicide', re.I),
    re.compile(r'medical advice', re.I),
    re.compile(r'hate speech', re.I),
]


def moderate_content(text: str) -> dict:
    issues = [p.pattern for p in BLOCKED_PATTERNS if p.search(text or '')]
    return {'approved': len(issues) == 0, 'issues': issues}
