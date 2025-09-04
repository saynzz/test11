def is_short_video(video_path: str, duration_threshold: int = 60) -> bool:
    """Проверяет, является ли видео Shorts (до 60 секунд)."""
    # Используем ffprobe (из ffmpeg) для получения длительности
    import subprocess
    cmd =  [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    duration = float(subprocess.check_output(cmd).decode().strip())
    return duration <= duration_threshold