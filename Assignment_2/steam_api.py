"""
Steam API Integration Module.
This module provides functions to interact with the Steam API for fetching game
information, including images, details, and app IDs.

"""

import json
import os
from typing import Dict, Optional
import requests

# Get the absolute path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def initialize_cache() -> Dict[str, int]:
    """
    Initialize the cache directory and load existing app ID cache if available.
    Return a dictionary mapping game names to their Steam app IDs
    """
    cache_dir = os.path.join(SCRIPT_DIR, "steam_cache")
    os.makedirs(cache_dir, exist_ok=True)

    cache_file = os.path.join(cache_dir, "app_id_cache.json")
    app_id_cache = {}

    # Load cache from file if it exists
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            app_id_cache = json.load(f)

    return app_id_cache


def save_cache(app_id_cache: Dict[str, int]) -> None:
    """
    Save the app ID cache to a file.
    app_id_cache: A dictionary mapping game names to their Steam app IDs
    """

    cache_dir = os.path.join(SCRIPT_DIR, "steam_cache")
    cache_file = os.path.join(cache_dir, "app_id_cache.json")

    with open(cache_file, 'w') as f:
        json.dump(app_id_cache, f)


def search_game_app_id(game_name: str) -> Optional[int]:
    """
    Search for a game's Steam App ID using the Steam Store API.
    Steam App ID or None if not found

    game_name: The name of the game to search for
    """

    # initializing cache
    global APP_ID_CACHE
    if not APP_ID_CACHE:
        APP_ID_CACHE = initialize_cache()

    # check cache first
    if game_name in APP_ID_CACHE:
        return APP_ID_CACHE[game_name]

    # search API
    search_url = "https://store.steampowered.com/api/storesearch"
    params = {
        "term": game_name,
        "l": "english",
        "cc": "US"
    }

    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("total", 0) > 0:
            app_id = data["items"][0]["id"]
            APP_ID_CACHE[game_name] = app_id
            save_cache(APP_ID_CACHE)
            return app_id

        return None
    except (requests.RequestException, json.JSONDecodeError, KeyError, IndexError):
        return None


def get_game_image_url(game_name: str) -> str:
    """
    Get the image URL for a game from Steam.
    URL of the game image or a placeholder URL if not found
    game_name: Name of the game
    """

    app_id = search_game_app_id(game_name)

    if app_id:
        # Use header image from Steam
        return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"

    # otherwise use placeholder with game name
    return f"https://placehold.co/600x300?text={game_name.replace(' ', '+')}"


def get_game_details(game_name: str) -> Dict:
    """
    Get detailed information about a game from Steam.
    Dictionary with game details or empty dict if not found

    game_name: Name of the game
    """

    app_id = search_game_app_id(game_name)

    if not app_id:
        return {"name": game_name, "header_image": get_game_image_url(game_name)}

    # Use API to get details
    details_url = "https://store.steampowered.com/api/appdetails"
    params = {
        "appids": app_id,
        "cc": "US",
        "l": "english"
    }

    response = requests.get(details_url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data and data.get(str(app_id), {}).get("success", False):
        game_data = data[str(app_id)]["data"]

        # Extract relevant information
        return {
            "name": game_data.get("name", game_name),
            "description": game_data.get("short_description", ""),
            "header_image": game_data.get("header_image", get_game_image_url(game_name)),
            "developers": game_data.get("developers", []),
            "publishers": game_data.get("publishers", []),
            "release_date": game_data.get("release_date", {}).get("date", "Unknown"),
            "genres": [genre.get("description", "") for genre in game_data.get("genres", [])]
        }

    return {"name": game_name, "header_image": get_game_image_url(game_name)}


# Global variables
APP_ID_CACHE = {}


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta

    python_ta.check_all(config={
        'extra-imports': [
            'requests', 'json', 'os', 'typing'
        ],
        'allowed-io': ['app_id_cache.json'],
        'max-line-length': 120,
        'disable': ['E9997', 'E9998']
    })
