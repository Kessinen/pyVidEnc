from subprocess import run
from pathlib import Path
from argparse import ArgumentParser
from rich import print

from parse_video import get_video_data
from movie_info import fetch_movie_info
from models import VideoData, OMDBVideoInfo

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("-t","--title", type=str, default=None, required=False)
    parser.add_argument("-i","--imdb_id", type=str, default=None, required=False)
    parser.add_argument("-y","--year", type=int, default=None, required=False)


    parsed_args = parser.parse_args()
    if not parsed_args.input_file.exists():
        raise FileNotFoundError(parsed_args.input_file)
    
    return parser.parse_args()

def fetch_poster(filename: str, url: str, output_name = None):
    # TODO: Add error handling. What if ie 404 error is returned.
    image_suffix = Path(url).suffix
    output_filename = Path(filename).stem + "-thumbnail" + image_suffix
    if output_name:
        output_filename = output_name + image_suffix
    run(["wget", "-O", output_filename, url], capture_output=True)

def output_filename_format(movie_info: OMDBVideoInfo):
    title = movie_info.Title.title().replace(" ", "")
    imdb_id = movie_info.imdbID
    year = movie_info.Year
    filename = [title, year, imdb_id]
    return ".".join([str(x) for x in filename if x])

def confirm_video_info(movie_info: OMDBVideoInfo):
    print(f"""Found the following video info from OMDB:

Title: {movie_info.Title}
Year: {movie_info.Year}
IMDB: https://www.imdb.com/title/{movie_info.imdbID}""")
    confirm = input("Is this correct? (Y/n) ")
    return confirm.lower() != "n"
    
def main():
    args = parse_args()
    video_data: VideoData = get_video_data(args.input_file)

    video_info_fields = {k:v for k,v in {"title":args.title, "imdb_id":args.imdb_id, "year":args.year}.items() if v}
    movie_info = fetch_movie_info(**video_info_fields)

    if movie_info and confirm_video_info(movie_info):
        output_filename_stem = output_filename_format(movie_info)
        Path(f"{output_filename_stem}.json").write_text(movie_info.model_dump_json())
        fetch_poster(args.input_file, movie_info.Poster, output_filename_stem)

if __name__ == "__main__":
    main()