"""
Steam API Integration Module.
This module provides functions to interact with the Steam API for fetching game
information, including images, details, and app IDs.

"""
import requests
import json
import os
from typing import Dict, Optional


def initialize_cache() -> Dict[str, int]:
    """Initialize the cache directory and load existing app ID cache if available.

    Returns:
        A dictionary mapping game names to their Steam app IDs
    """
    cache_dir = "steam_cache"
    os.makedirs(cache_dir, exist_ok=True)

    cache_file = os.path.join(cache_dir, "app_id_cache.json")
    app_id_cache = {}

    # Load cache from file if it exists
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                app_id_cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            app_id_cache = {}

    return app_id_cache


def save_cache(app_id_cache: Dict[str, int]) -> None:
    """Save the app ID cache to a file.

    Args:
        app_id_cache: A dictionary mapping game names to their Steam app IDs
    """
    cache_dir = "steam_cache"
    cache_file = os.path.join(cache_dir, "app_id_cache.json")

    with open(cache_file, 'w') as f:
        json.dump(app_id_cache, f)


def search_game_app_id(game_name: str) -> Optional[int]:
    """Search for a game's Steam App ID using the Steam Store API.

    Args:
        game_name: The name of the game to search for

    Returns:
        Steam App ID or None if not found
    """
    # Ensure the cache is initialized
    global APP_ID_CACHE
    if not APP_ID_CACHE:
        APP_ID_CACHE = initialize_cache()

    # Check cache first
    if game_name in APP_ID_CACHE:
        return APP_ID_CACHE[game_name]

    # Search API
    search_url = f"https://store.steampowered.com/api/storesearch"
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
    """Get the image URL for a game from Steam.

    Args:
        game_name: Name of the game

    Returns:
        URL of the game image or a placeholder URL if not found
    """
    app_id = search_game_app_id(game_name)

    if app_id:
        # Use header image from Steam
        return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"

    # Fallback to placeholder with game name
    return f"https://placehold.co/600x300?text={game_name.replace(' ', '+')}"


def get_game_details(game_name: str) -> Dict:
    """Get detailed information about a game from Steam.

    Args:
        game_name: Name of the game

    Returns:
        Dictionary with game details or empty dict if not found
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

    try:
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
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        pass

    return {"name": game_name, "header_image": get_game_image_url(game_name)}


# Global variables
APP_ID_CACHE = {}
