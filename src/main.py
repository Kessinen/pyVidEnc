from subprocess import run
from pathlib import Path
from argparse import ArgumentParser
from typing import Union, List
import json

from rich import print

from models import VideoStream, AudioStream, SubtitleStream, GeneralVideoData, VideoData

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input-file", type=Path)
    #parser.add_argument("--output_path", type=Path)
    return parser.parse_args()

def runcmd(cmd: List) -> Union[str, None]:
    runcmd = run(cmd, capture_output=True)
    if runcmd.returncode != 0:
        return None
    return runcmd.stdout.decode("utf-8")

def get_video_streams(video_path) -> List[VideoStream]:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-select_streams", "v", str(video_path)]
    retval = runcmd(cmd)
    if not retval:
        return None
    json_data = json.loads(retval)
    if "streams" not in json_data:
        return None
    return_data = [VideoStream(**stream) for stream in json_data["streams"]]
    return return_data

def get_audio_streams(video_path) -> List[AudioStream]:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-select_streams", "a", str(video_path)]
    retval = runcmd(cmd)
    if not retval:
        return None
    json_data = json.loads(retval)
    if "streams" not in json_data:
        return None
    return_data = [AudioStream(**stream) for stream in json_data["streams"]]
    return return_data

def get_subtitle_streams(video_path) -> List[SubtitleStream]:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-select_streams", "s", str(video_path)]
    retval = runcmd(cmd)
    if not retval:
        return {}
    json_data = json.loads(retval)
    if "streams" not in json_data:
        return None
    return_data = [SubtitleStream(**stream) for stream in json_data["streams"]]
    return return_data

def get_general_video_info(video_path) -> dict:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(video_path)]
    data = runcmd(cmd)
    if not data:
        return None
    json_data = json.loads(data)
    if "format" not in json_data:
        return None
    return GeneralVideoData(**json_data["format"])


def get_video_data(video_path) -> dict:
    data = {
        "video_streams": get_video_streams(video_path),
        "audio_streams": get_audio_streams(video_path),
        "subtitle_streams": get_subtitle_streams(video_path),
        "general_video_info": get_general_video_info(video_path),
    }
    return VideoData(**data)
    
    
def main():
    args = parse_args()
    if not args.input_file.exists():
        raise FileNotFoundError(args.input_file)
    jee = get_video_data(args.input_file)
    
    json.dump(jee.model_dump(), open(f"{args.input_file.stem}.json", "w"), indent=4)

if __name__ == "__main__":
    main()