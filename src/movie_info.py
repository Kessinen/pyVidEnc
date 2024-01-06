from rich import print
import requests

from settings import OMDB_API_KEY
from models import OMDBVideoInfo

base_url = "http://www.omdbapi.com"

def fetch_movie_info(title: str = None, imdb_id: str = None, year: int = None) -> OMDBVideoInfo:
    if OMDB_API_KEY == None:
        print("Error: OMDB_API_KEY is not set")
        return None
    
    if title == None and imdb_id == None:
        print("Title or Imdb_id is required")
        return None
    params = {}
    if title:
        params["t"] = title
    if imdb_id:
        params["i"] = imdb_id
    if year:
        params["y"] = year
    params["apikey"] = OMDB_API_KEY
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    json_data = response.json()
    if json_data["Response"] == "False":
        print(f"Error: {json_data['Error']}")
        return None
    # Convert N/A to None
    json_data = {k:None if x == "N/A" else x for k,x in json_data.items()}
    return OMDBVideoInfo(**json_data)