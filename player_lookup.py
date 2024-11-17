# player_lookup.py
import requests
import json

# Fetch play-by-play data and build player dictionary
def create_player_id_to_player_dictionary(game_id):
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data and "rosterSpots" in data:
            # Create player dictionary with player ID as key and full name as value
            players = data["rosterSpots"]
            player_dict = {player['playerId']: player for player in players}
            return player_dict
        else:
            print("No 'rosterSpots' data available.")
            return None
    else:
        print(f"Failed to fetch play-by-play data for game ID {game_id}")
        return None



import requests
import json


# Fetch game data
def fetch_game_data(game_id):
    print(f"Fetching game data...")
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    response = requests.get(url)
    if response.status_code == 200:
        print("Fetch request successful")
        return response.json()
    else:
        print(f"Failed to fetch play-by-play data for game ID {game_id}")
        print(f"Request URL: {url}")
        return None
"""
# Create playerId to player dictionary and return it
def create_player_id_to_player_dictionary(game_id):
    data = fetch_game_data(game_id)
    if data and "rosterSpots" in data:
        players = data["rosterSpots"]
        
        # Create and return dictionary from player IDs
        player_dict = {player['playerId']: player for player in players}
        print(player_dict)
        return player_dict
    else:
        print("No 'rosterSpots' data available.")
        return None

# Call the function and store the returned dictionary in a variable
player_dict = create_player_id_to_player_dictionary(game_id)




# Now you can access the dictionary outside of the function
print(f"Looking for player_id: {player_id}")
if player_dict and player_id in player_dict:
    print(f"Player entry for player_id {player_id}:")
    print(player_dict[player_id])
    print(player_dict[player_id]['firstName']['default'])
else:
    print(f"Player ID {player_id} not found in the data.")
    print("Available player IDs in the dictionary:")
    print(player_dict.keys())
"""
