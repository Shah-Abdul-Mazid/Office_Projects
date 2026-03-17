from datetime import timezone
from email.utils import format_datetime
from typing import Sequence
from urllib.parse import urljoin
from xml.etree.ElementTree import Element, SubElement, tostring

from app.core.config import get_settings
from app.models.episode import Episode

settings = get_settings()
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"


def _absolute_url(base_url: str, maybe_relative: str | None) -> str:
    if not maybe_relative:
        return ""
    if maybe_relative.startswith("http://") or maybe_relative.startswith("https://"):
        return maybe_relative
    return urljoin(base_url, maybe_relative.lstrip("/"))


def build_podcast_rss(episodes: Sequence[Episode], base_url: str) -> str:
    rss = Element(
        "rss",
        attrib={
            "version": "2.0",
            "xmlns:itunes": ITUNES_NS,
        },
    )
    channel = SubElement(rss, "channel")

    channel_link = str(settings.public_base_url or base_url).rstrip("/")
    SubElement(channel, "title").text = settings.podcast_title
    SubElement(channel, "link").text = channel_link
    SubElement(channel, "description").text = settings.podcast_description
    SubElement(channel, "language").text = settings.podcast_language
    SubElement(channel, f"{{{ITUNES_NS}}}author").text = settings.podcast_author
    SubElement(channel, f"{{{ITUNES_NS}}}summary").text = settings.podcast_description
    SubElement(channel, f"{{{ITUNES_NS}}}explicit").text = settings.podcast_explicit
    SubElement(channel, f"{{{ITUNES_NS}}}category", attrib={"text": settings.podcast_category})

    if settings.podcast_image_url:
        SubElement(channel, f"{{{ITUNES_NS}}}image", attrib={"href": str(settings.podcast_image_url)})

    for episode in episodes:
        item = SubElement(channel, "item")
        audio_url = _absolute_url(channel_link, episode.audio_url)
        published_at = episode.published_at or episode.created_at
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)

        SubElement(item, "title").text = episode.topic
        SubElement(item, "description").text = f"A Guide and Student explore: {episode.topic}"
        SubElement(item, "guid").text = str(episode.id)
        SubElement(item, "pubDate").text = format_datetime(published_at.astimezone(timezone.utc))
        SubElement(
            item,
            "enclosure",
            attrib={
                "url": audio_url,
                "length": str(episode.audio_size_bytes or 0),
                "type": "audio/mpeg",
            },
        )
        SubElement(item, f"{{{ITUNES_NS}}}author").text = settings.podcast_author
        SubElement(item, f"{{{ITUNES_NS}}}summary").text = f"A Guide and Student explore: {episode.topic}"
        SubElement(item, f"{{{ITUNES_NS}}}explicit").text = settings.podcast_explicit

    return tostring(rss, encoding="utf-8", xml_declaration=True).decode("utf-8")
