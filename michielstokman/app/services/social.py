from __future__ import annotations

import os
from typing import Dict
from app.config import settings
from app.schemas import StoryResponse

async def post_to_social_media(story: StoryResponse) -> Dict[str, str]:
    """
    Automates posting to Facebook and Instagram via Meta Graph API.
    Currently implements a mock/placeholder system as per Phase 3 requirements.
    """
    results = {}
    
    # Facebook Posting Logic
    fb_token = os.getenv("META_FACEBOOK_TOKEN")
    if fb_token:
        # Placeholder for actual Graph API call
        # endpoint = f"https://graph.facebook.com/v19.0/{settings.fb_page_id}/feed"
        results["facebook"] = "Successfully queued for Facebook posting (Mock)"
    else:
        results["facebook"] = "Skipped: META_FACEBOOK_TOKEN not configured"

    # Instagram Posting Logic
    ig_token = os.getenv("META_INSTAGRAM_TOKEN")
    if ig_token:
        # Placeholder for actual Graph API call
        results["instagram"] = "Successfully queued for Instagram posting (Mock)"
    else:
        results["instagram"] = "Skipped: META_INSTAGRAM_TOKEN not configured"

    return results

def get_social_copy(story: StoryResponse) -> Dict[str, str]:
    """
    Generates platform-specific copy for social media.
    """
    summary = story.episode_text[:200].strip() + "..."
    return {
        "facebook_copy": f"New Meditation Episode: {story.title}\n\n{summary}\n\nListen now on Spotify!",
        "instagram_copy": f"✨ {story.title} ✨\n\nTake a moment for yourself today. {summary}\n\n#Meditation #Mindfulness #AI #Podcast",
    }
