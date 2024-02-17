from pathlib import Path
from argparse import ArgumentParser
from rich import print
from rich.progress import track
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
    number_of_files = len(video_list)
    for videofile in track(video_list, description=f"Found {number_of_files} files. Indexing..."):

        try:
            video_data = get_video_data(videofile)
            video_data_add = {
                "Title": video_data.general_video_info.tags.title,
                "date_released": video_data.general_video_info.tags.DATE_RELEASED,
                "imdb_id": video_data.general_video_info.tags.IMDB_ID,
                "original_media_type": "",
                "Filename": videofile.name,
                "Filesize": videofile.stat().st_size,
                "MPixels": video_data.video_streams[0].MPixels,
                "Codec": video_data.video_streams[0].codec_name,
                "Format": video_data.general_video_info.format_name,
                "Resolution": f"{video_data.video_streams[0].width}x{video_data.video_streams[0].height}",
                "FPS": round(video_data.video_streams[0].fps, 2)
            }

            video_list_data.append(video_data_add)
        except Exception as e:
            print("Video giving error: ", videofile, "Codec: ", video_data.video_streams[0].codec_name,"\n")
            print(e)
    return video_list_data

def write_csv(video_list_data):
    with open("video_index.csv", "w") as f:
        writer = DictWriter(f, fieldnames=video_list_data[0].keys())
        writer.writeheader()
        writer.writerows(video_list_data)

def write_json(video_list_data):
    with open("video_index.json", "w") as f:
        json.dump(video_list_data, f, indent=4)

def main()->None:
    args = parse_args()
    videofile_list: List[Path] = get_videofile_list(args.input_folder)
    indexed_list = index_video_files(videofile_list)
    print("Indexing complete!")
    write_csv(indexed_list)
    write_json(indexed_list)
        

    

if __name__ == "__main__":
    main()