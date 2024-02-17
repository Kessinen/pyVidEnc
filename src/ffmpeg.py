from subprocess import run
from pydantic import BaseModel, Field
from pathlib import Path
from typing import List

from models import VideoData, OMDBVideoInfo
from settings import render_settings

class ffmpegEncodeCMD(BaseModel):
    video_file: VideoData
    metadata: OMDBVideoInfo
    #output_file: Path = Field(default_factory=lambda: Path(video_file.filename).with_suffix(".mp4"))

    def set_output_filename(self, suffix: str = ".mkv") -> Path:
        output_filename = "output.mkv"
        if not self.metadata:
            return output_filename
        
        invalid_chars = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|", " "]
        output_filename = f"{self.metadata.Title}.{self.metadata.Year}".title() + suffix
        for char in invalid_chars:
            output_filename = output_filename.replace(char, "_").replace("__", "_")
        return output_filename

    def set_video_render_settings(self) -> List[str]:
        # Get current fps
        fps = int(self.video_file.video_streams[0].r_frame_rate.split("/")[0])
        render_settings = ["-c:v", "libsvtav1", "-crf", "35", "-preset", "6", "-svtav1-params", "tune=0,enable-overlay=1,film-grain=30", "-g", str(fps*10)]
        if self.video_file.video_streams[0].sample_aspect_ratio != "1:1":
            correctDar = (self.video_file.video_streams[0].display_aspect_ratio.split(":"))
            new_resolution = (int(self.video_file.video_streams[0].height / int(correctDar[1]) * int(correctDar[0])), self.video_file.video_streams[0].height)
            render_settings += ["-vf", f"scale={'x'.join(str(x) for x in new_resolution)}:flags=lanczos"]
        return render_settings

    def set_audio_render_settings(self) -> List[str]:
        return_value = list()
        for i, audiostream in enumerate(self.video_file.audio_streams): #self.video_file.audio_streams:
            if audiostream.codec_name != "opus":
                return_value += [f"-c:a:{i}", "libopus"]
                if audiostream.channel_layout == "5.1(side)":
                    return_value += [f"-filter:a:{i}", "channelmap=channel_layout=5.1"]
            return_value += [f"-metadata:s:a:{i}", f"language={audiostream.tags.language}"]
            return_value += [f"-metadata:s:a:{i}", f"title='{audiostream.tags.title}'"]
        return return_value

    def set_subtitle_render_settings(self) -> List[str]:

        return_value = list()
        if self.video_file.subtitle_streams:
            return_value += [f"-c:s", "copy"]
        for i, subtitlestream in enumerate(self.video_file.subtitle_streams):
            if "language" in subtitlestream.tags:
                return_value += [f"-metadata:s:s:{i}", f"language={subtitlestream.tags['language']}"]
        return return_value

    def set_metadata_render_settings(self) -> List[str]:
        return_value = list()
        return_value += ["-metadata", f"title='{self.metadata.Title}'"]
        if self.metadata.Year:
            date_released = f"{self.metadata.Year}"
        if self.metadata.Released:
            date_released = self.metadata.Released
        return_value += ["-metadata", f"date_released='{date_released}'"]
        if self.metadata.imdbID:
            return_value += ["-metadata", f"imdb_id='{self.metadata.imdbID}'"]
        return return_value

    def encode(self) -> str:
        base_cmd = ["ffmpeg", "-v", "error", "-i", f"'{self.video_file.general_video_info.filename}'", "-map", "0", "-map_metadata", "-1", "-pix_fmt", "yuv420p10le"]
        output_filename = [f"'{self.set_output_filename()}'"]
        video_render_settings = self.set_video_render_settings()
        audio_render_settings = self.set_audio_render_settings()
        subtitle_render_settings = self.set_subtitle_render_settings()
        cmd = base_cmd + video_render_settings + audio_render_settings + subtitle_render_settings + self.set_metadata_render_settings() + output_filename
        print("Command to run:\n", " ".join(cmd).strip())
        return " ".join(cmd).strip()
        

    