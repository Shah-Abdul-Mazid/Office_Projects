def story_prompt(title: str, growth_area: str, life_phase: str, min_words: int, max_words: int) -> str:
    return f"""You are writing for Transform to Liberation.
Write a first-person emotional story titled \"{title}\".
Constraints:
- Word count: {min_words}-{max_words}
- Growth area focus: {growth_area}
- Life phase: {life_phase}
- Tone: grounded, humane, emotionally safe, hopeful
- Include one subtle liberation turning point
Output strict JSON with keys: title,type,language,growth_area,life_phase,content"""


def meditation_prompt(title: str, growth_area: str, life_phase: str, minutes: int = 7) -> str:
    return f"""You are writing for Transform to Liberation.
Write a second-person guided meditation titled \"{title}\".
Constraints:
- Target length: ~{minutes} minutes spoken pace
- Growth area focus: {growth_area}
- Life phase: {life_phase}
- Include breath guidance, body awareness, gentle close
Output strict JSON with keys: title,type,language,growth_area,life_phase,content"""
