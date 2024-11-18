#game_monitor_utils.py
import json
import requests
from datetime import datetime, timezone
import time

number_of_api_calls = 0

#Number of API calls getters

def get_number_of_api_calls():
    return number_of_api_calls

def increment_api_calls():
    global number_of_api_calls
    number_of_api_calls += 1
    # print(f"Number of API calls: {number_of_api_calls}")

# Load game details from file
def load_game_details(file_path):
    game_details = {}
    
    with open(file_path, 'r') as file: 
        for line in file:
            if line.startswith('Game Id:'):
                game_details['game_id'] = line.split(':')[1].strip()
            elif line.startswith('Start Time (UTC):'):
                # Parse the start time as an aware datetime in UTC
                start_time_str = line.split(': ', 1)[1].strip()
                game_details['start_time'] = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            elif line.startswith('Home Team:'):
                game_details['home_team'] = line.split(':')[1].strip()
            elif line.startswith('Away Team:'):
                game_details['away_team'] = line.split(':')[1].strip()
            elif line.startswith('Play-by-Play API URL: '):
                game_details['play_by_play_api_URL'] = line.split(':')[1].strip() + ":" + line.split(':')[2].strip()
    print(f'Loaded Game Details: {game_details} \n')
    print(f"{game_details['play_by_play_api_URL']} \n\n")
    
    return game_details

# Wait until the game start time before starting the monitor
def wait_until_game_start(start_time):
    while True:
        current_time = datetime.now(timezone.utc)  # Get current time as UTC-aware
        time_to_start = (start_time - current_time).total_seconds()
        minutes_to_start = time_to_start / 60
        hours_to_start = minutes_to_start  / 60
        
        #print(f"hours to start: {hours_to_start} \n")
        #print(f"minutes to start: {minutes_to_start} \n")
        
        if time_to_start <= 0:
            break

        if hours_to_start > 1 :  # Check if time to start is > 1 hour
            
            print(f"Game starts in {int(hours_to_start)} hour(s) and . Waiting...")
            time.sleep(3500) # check in 60 minutes
        elif int(minutes_to_start) > 30 :
            print(f"Game starts in {int(minutes_to_start)} minutes. Waiting...")
            time.sleep(1800)  # Check in 30 minutes
        elif int(minutes_to_start) > 15 :
            print(f"Game starts in {int(minutes_to_start)} minutes. Waiting...")
            time.sleep(900)
        elif int(minutes_to_start) > 5 :
            print(f"Game starts in {int(minutes_to_start)} minutes. Waiting...")
            time.sleep(300)
        elif int(minutes_to_start) > 1 :
            print(f"Game starts in {int(minutes_to_start)} minutes. Waiting...")
            time.sleep(30)
        else :
            print(f"Game Starts Soon...")
            time.sleep(time_to_start)

# Fetch play-by-play data for the game
def fetch_play_by_play(game_id):
    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"  
    response = requests.get(url)
    increment_api_calls()
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch play-by-play data for game ID {game_id}")
        print(f"Request URL: {url}")
        return None
    
# Log game event JSON to game file

def log_json_to_game_file(game_file, event, player_dict):
    with open(game_file, 'a') as file:
        event_type = event.get("typeDescKey", "unknown")
        time_in_period = event.get("timeInPeriod", "unknown")
        period = event["periodDescriptor"].get("number", "unknown")
        team_id = event["details"].get("eventOwnerTeamId", "unknown") if "details" in event else "unknown"
        number_of_api_calls = get_number_of_api_calls()
        
        player_id = None
        if "details" in event and "scoringPlayerId" in event["details"]:
            player_id = event["details"]["scoringPlayerId"]
        
        if player_id and player_id in player_dict:
            player_name = player_dict[player_id]["lastName"]["default"]
        else:
            player_name = "Unknown Player"

        file.write(f"API Calls: {number_of_api_calls}")
        file.write(f"Period: {period}, Time in Period: {time_in_period} ")
        file.write(f"Event Type: {event_type} ")
        file.write(f"Team ID: {team_id} ")
        file.write(f"Player: {player_name} ")
        file.write("Details:\n")
        file.write(json.dumps(event, indent=2))  # Write the full play details in JSON format
        file.write("\n\n")
        
