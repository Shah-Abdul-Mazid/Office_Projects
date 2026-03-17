from enum import StrEnum


class SpeakerRole(StrEnum):
    GUIDE = "GUIDE"
    STUDENT = "STUDENT"


class ScriptStatus(StrEnum):
    QUEUED = "queued"
    GENERATING = "generating"
    TTS_PENDING = "tts_pending"
    TTS_PROCESSING = "tts_processing"
    READY = "ready"
    FAILED = "failed"


class JobType(StrEnum):
    SCRIPT_GENERATION = "script_generation"
    TTS_RENDER = "tts_render"
    AUDIO_STITCH = "audio_stitch"


class ProcessingStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AudioAssetType(StrEnum):
    SEGMENT = "segment"
    MIXDOWN = "mixdown"
    MANIFEST = "manifest"
