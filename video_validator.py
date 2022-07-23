import os
import magic
from moviepy.editor import VideoFileClip


def validate_video(path):
    """
    Check if the file size if <1GB and if the video length is less than 10 minutes.
    And also if the video format is mp4 or mkv.
    Returns (isInvalid, Error Message if invalid, Data [size, duration] if valid)
    """
    clip = VideoFileClip(path)
    duration = clip.duration
    size = os.path.getsize(path)
    filetype = magic.from_file(path, mime=True)

    if duration > 10 * 60:
        return True, "Video is too long. (Max 10 minutes)", None

    if size > 1e9:
        return True, "Video is too large. (Max 1GB)", None

    if filetype not in ["video/mp4", "video/x-matroska"]:
        return True, "Video format is not supported. (Only mp4 and mkv)", None

    return False, None, (size, duration)
