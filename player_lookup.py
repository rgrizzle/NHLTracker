# player_lookup.py
import requests
import json

class Team:
    def __init__(self,team_id, team_name, team_name_abbreviated, home_or_away):
        self.team_id = team_id
        self.team_name = team_name
        self.team_name_abbreviated = team_name_abbreviated
        self.home_or_away = home_or_away



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
    
    
# Modify create_teams to return the teams dictionary
def create_teams(game_id):
    teams = {}  # Initialize a local dictionary to hold the teams
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if "awayTeam" in data:
            # Create the away team object
            away_team = Team(
                team_id=data["awayTeam"].get("id"),
                team_name=data["awayTeam"]["name"].get("default"),
                team_name_abbreviated=data["awayTeam"].get("abbrev"),
                home_or_away="away"
            )
            teams[away_team.team_id] = away_team  # Use away_team.team_id as the key
        
        if "homeTeam" in data:
            # Create the home team object
            home_team = Team(
                team_id=data["homeTeam"].get("id"),
                team_name=data["homeTeam"]["name"].get("default"),
                team_name_abbreviated=data["homeTeam"].get("abbrev"),
                home_or_away="home"
            )
            teams[home_team.team_id] = home_team  # Use home_team.team_id as the key

        return teams  # Return the populated dictionary
    else:
        print(f"Failed to fetch play-by-play data for game ID {game_id}")
        return None


# Define the function to return the teams dictionary
def create_teams_dict(game_id):
    teams_dict = create_teams(game_id)  # Call create_teams and store the result
    return teams_dict


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

# create team dict

