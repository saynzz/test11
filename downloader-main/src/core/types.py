from dataclasses import dataclass

@dataclass
class QualityPreset:
    name: str
    max_height: int
    fps: int
    bitrate: str

PRESETS = {
    "1080p": QualityPreset("1080p", 1080, 60, "10M"),
    "720p": QualityPreset("720p", 720, 30, "5M"),
    "max": QualityPreset("max", 9999, 999, "best"),
}