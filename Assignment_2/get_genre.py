import steamspypi
import json


def get_game_info(app_id):
    """
    Get the genre of a game from Steam.
    app_id: The app ID of the game to get the genre of.
    """

    data = {
        "request": "appdetails",
        "appid": str(app_id)
    }
    try:
        result = steamspypi.download(data)
        if result and "genre" in result:
            return result["genre"]
        return "Unknown"
    except Exception as e:
        print(f"Error fetching data for App ID {app_id}: {e}")
        return "Error"


with open("unique_games_output.json", "r", encoding="utf-8") as file:
    game_list = json.load(file)

classified_games = []

for game in game_list:
    game_name = game.get("item_name", "Unknown")
    app_id = game.get("item_id", "0")
    genre = get_game_info(app_id)
    game["genre"] = genre
    classified_games.append(game)
    print(f"Processed: {game_name} (App ID: {app_id}) -> {genre}")

with open("classified_games.json", "w", encoding="utf-8") as json_file:
    json.dump(classified_games, json_file, ensure_ascii=False, indent=4)

print("complete")