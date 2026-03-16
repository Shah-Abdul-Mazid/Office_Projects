def generate_json_from_prompt(prompt: str) -> dict:
    is_meditation = 'guided meditation' in prompt.lower()
    return {
        'title': 'A Gentle Return' if is_meditation else 'The Door I Finally Opened',
        'type': 'meditation' if is_meditation else 'story',
        'language': 'en',
        'growth_area': 'Fear & Freedom',
        'life_phase': 'Recalibrating',
        'content': 'Close your eyes if that feels safe...' if is_meditation else 'I used to think freedom had to be loud...'
    }
