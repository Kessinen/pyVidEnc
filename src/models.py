from pydantic import BaseModel, Field, validator
from typing import List, Optional

class AudioTags(BaseModel):
    language: str
    title: str

class GeneralVideoDataTags(BaseModel):
    title: str
    IMDB_ID: str
    DATE_RELEASED: str

class VideoStream(BaseModel):
    index: int
    codec_name: str
    codec_long_name: str
    sample_aspect_ratio: str
    display_aspect_ratio: str
    pix_fmt: str
    disposition: dict
    tags: dict

    # TODO: SAR and DAR converters may not be the best way to do this. Thus, they are commented out. Review needed.
    # @validator("sample_aspect_ratio")
    # def validate_sample_aspect_ratio(cls, value):
    #     values = value.split(':')
    #     if len(values) != 2:
    #         raise ValueError('Input must be in the format "int:int"')
    #     return (int(values[0]), int(values[1]))

    # @validator("display_aspect_ratio")
    # def validate_display_aspect_ratio(cls, value):
    #     values = value.split(':')
    #     if len(values) != 2:
    #         raise ValueError('Input must be in the format "int:int"')
    #     return (int(values[0]), int(values[1]))

    @validator("disposition")
    def validate_disposition(cls, value):
        return_value = {k: v for k, v in value.items() if v == 1}
        return return_value

class AudioStream(BaseModel):
    index: int
    codec_name: str
    codec_long_name: str
    sample_fmt: str
    sample_rate: int
    channels: int
    channel_layout: str
    disposition: dict
    tags: AudioTags

    @validator("disposition")
    def validate_disposition(cls, value):
        return_value = {k: v for k, v in value.items() if v == 1}
        return return_value

class SubtitleStream(BaseModel):
    index: int
    codec_name: str
    codec_long_name: str
    tags: dict

class GeneralVideoData(BaseModel):
    filename: str
    format_name: str
    format_long_name: str
    duration: float
    tags: GeneralVideoDataTags

class VideoData(BaseModel):
    video_streams: List[VideoStream]
    audio_streams: List[AudioStream] = Field(default=None)
    subtitle_streams: List[SubtitleStream] = Field(default=None)
    general_video_info: GeneralVideoData