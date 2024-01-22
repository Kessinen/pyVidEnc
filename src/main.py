from subprocess import run
from pathlib import Path
from argparse import ArgumentParser
from rich import print

from parse_video import get_video_data
from movie_info import fetch_movie_info
from models import VideoData, OMDBVideoInfo
from ffmpeg import ffmpegEncodeCMD

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("-t","--title", type=str, default=None, required=False)
    parser.add_argument("-i","--imdb_id", type=str, default=None, required=False)
    parser.add_argument("-y","--year", type=int, default=None, required=False)
    parser.add_argument("-p","--poster", action="store_true", default=False, required=False, help="Download the movie poster")
    parser.add_argument("-j","--json", action="store_true", default=False, required=False, help="Write the movie info to a json file")

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
    
def writeShellScript(filename: Path, cmd: str):
    if filename.exists():
        print(f"{filename} already exists. Skipping shell script generation.")
    with open (filename, "w") as f:
        f.write(cmd)
    print(f"Writing shell script to {filename}")
    pass

def main():

    #Parse command line arguments
    print("Parsing command line arguments...")
    args = parse_args()

    # Get video data and save it to a pydantic model
    print("Getting video data...")
    video_data: VideoData = get_video_data(args.input_file)

    # Get movie info from OMDB and save it to a pydantic model
    print("Fetching movie info...")
    movie_info = fetch_movie_info(title=args.title, imdb_id=args.imdb_id, year=args.year)

    # Encode the video
    print(f"Encoding {args.input_file}")
    jee = ffmpegEncodeCMD(video_file=video_data, metadata=movie_info)
    cmd = jee.encode()
    writeShellScript(args.input_file.parent / "encode.sh", cmd=cmd)


    # Set the output filename based on the info we have. Also get the poster and save the movies OMDB info to a json file.
    print("Setting the output filename...")
    if movie_info:
        output_filename_stem = output_filename_format(movie_info)
    if args.json:
        Path(f"{output_filename_stem}.json").write_text(movie_info.model_dump_json())
    if args.poster:
        fetch_poster(args.input_file, movie_info.Poster, output_filename_stem)

if __name__ == "__main__":
    main()