#game_monitor_utils.py
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

    print(f'Loaded Game Details: {game_details}')
    return game_details

# Wait until the game start time before starting the monitor
def wait_until_game_start(start_time):
    while True:
        current_time = datetime.now(timezone.utc)  # Get current time as UTC-aware
        time_to_start = (start_time - current_time).total_seconds()
        
        if time_to_start <= 0:
            break

        if int(time_to_start) / 60 > 3600:  # Check if time to start is > 1 hour
            hours_to_start = time_to_start / 60
            print(f"Game starts in {int(hours_to_start)} hours. Waiting...")
            time.sleep(3500)
        else:
            minutes_to_start = time_to_start / 60
            print(f"Game starts in {int(minutes_to_start)} minutes. Waiting...")
            time.sleep(300)  # Check every 5 minutes

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