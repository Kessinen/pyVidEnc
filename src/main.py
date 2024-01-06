from subprocess import run
from pathlib import Path
from argparse import ArgumentParser
from rich import print

from parse_video import get_video_data
from models import VideoData

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input-file", type=Path)

    parsed_args = parser.parse_args()
    if not parsed_args.input_file.exists():
        raise FileNotFoundError(parsed_args.input_file)
    
    return parser.parse_args()


    
    
def main():
    args = parse_args()
    video_data: VideoData = get_video_data(args.input_file)

if __name__ == "__main__":
    main()