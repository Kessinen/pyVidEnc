from pathlib import Path
from argparse import ArgumentParser
from rich import print
from csv import DictWriter
from typing import List
import json

from models import VideoData
from settings import valid_video_extensions
from parse_video import get_video_data

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("input_folder", type=Path)
    parsed_args = parser.parse_args()

    if not parsed_args.input_folder.exists():
        raise FileNotFoundError(parsed_args.input_folder)
    
    return parsed_args

def get_videofile_list(input_folder: Path):
    filelist = list()
    for extension in valid_video_extensions:
        filelist.extend(input_folder.glob(f"*{extension}"))
    return filelist

def index_video_files(video_list: List[Path]) -> dict:
    video_list_data = list()
    for i,videofile in enumerate(video_list):
        try:
            video_data = get_video_data(videofile)
            video_data_add = {
                "Filename": videofile.name,
                "Filesize": videofile.stat().st_size,
                "MPixels": video_data.video_streams[0].MPixels,
                "Codec": video_data.video_streams[0].codec_name,
                "Resolution": f"{video_data.video_streams[0].width}x{video_data.video_streams[0].height}",
                "FPS": round(video_data.video_streams[0].fps, 2)
            }
            video_list_data.append(video_data_add)
            print(f"{i+1}/{len(video_list)}")
        except Exception as e:
            print("Video giving error: ", videofile, "Codec: ", video_data.video_streams[0].codec_name,"\n")
            print(e)
    return video_list_data

def main()->None:
    args = parse_args()
    videofile_list: List[Path] = get_videofile_list(args.input_folder)
    files_found = len(videofile_list)
    print(f"Found {files_found} files.","Starting indexing...")
    indexed_list = index_video_files(videofile_list)
    print("Indexing complete!")
    with open("video_index.csv", "w") as f:
        writer = DictWriter(f, fieldnames=indexed_list[0].keys())
        writer.writeheader()
        writer.writerows(indexed_list)
        

    

if __name__ == "__main__":
    main()