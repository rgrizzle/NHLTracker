import requests
from datetime import datetime, timedelta
import os
import subprocess

# List of teams you're tracking (e.g., team names)
tracked_teams = ['San Jose']  # Modify as needed

# Function to fetch the NHL schedule for a specific day
def fetch_nhl_schedule(date):
    url = f"https://api-web.nhle.com/v1/schedule/{date}"  # Replace with correct API endpoint
    print(f'Request URL: {url}')
    response = requests.get(url)
    if response.status_code == 200:
        print(f'Request Successful')
        return response.json()
    else:
        print(f"Failed to fetch schedule for {date}")
        return None

# Function to create a game file for a specific game
def create_game_file(game_details):
    # Define file name and path
    directory = 'games'
    game_date = datetime.now().strftime("%Y-%m-%d")
    game_file = os.path.join(directory, f"{game_details['gameId']}_{game_details['away_team']['placeName']['default']}_at_{game_details['home_team']['placeName']['default']}_{game_date}.txt")
    game_monitor_script_path = r"D:\Projects\NHLTracker\game_monitor.py"
    
    # Check if the file already exists
    if os.path.exists(game_file):
        print(f"\n - Game file {game_file} already exists. Opening now... - \n")
        subprocess.Popen(["python3", game_monitor_script_path, game_file])
        return
    
    # Create a text file with game details
   
    with open(game_file, 'w') as f:
        f.write(f"Home Team: {game_details['home_team']['placeName']['default']}\n")
        f.write(f"Away Team: {game_details['away_team']['placeName']['default']}\n")
        f.write(f"Start Time (UTC): {game_details['start_time']}\n")
        f.write(f"Date: {game_details['date']}\n")
        f.write(f"Game Id: {game_details['gameId']}\n")
        f.write(f"\n")
    print(f"\n - Game file {game_file} created successfully. - \n")
    subprocess.Popen(["python3", game_monitor_script_path, game_file])
        

# Main function to check for games and create files
def check_and_create_game_files():
    # Get today's date
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    # Select target date, today or yesterday
    target_date = yesterday
    
    # convert target date to string
    target_date_string = target_date.strftime(('%Y-%m-%d'))
    
    # Fetch NHL schedule for today
    
    schedule_data = fetch_nhl_schedule(target_date_string)
    #print(f'Response: + {schedule_data}')
    
    if schedule_data:
        #Extract list of game weeks
        game_weeks = schedule_data.get('gameWeek', [])
        
        if game_weeks:
            
            games = game_weeks[0].get('games',[])
            print(f'Number of Games retrieved: {len(games)}')
            
            if games:
                
                # Iterate through games and check if any of the tracked teams are playing
                for game in games:
                    # Correctly extract the team names from the API response
                    game_id = str(game['id'])
                    venue = game['venue']['default']
                    home_team_name = game['homeTeam']['placeName']['default']
                    away_team_name = game['awayTeam']['placeName']['default']
                    print(f'GameID:' +  game_id + f' ' + away_team_name + ' at ' + home_team_name + ', ' + venue)
                    
                    # Check if the home or away team is in our tracked list
                    if home_team_name in tracked_teams or away_team_name in tracked_teams:
                        game_details = {
                            'home_team': game['homeTeam'],
                            'away_team': game['awayTeam'],
                            'start_time': game['startTimeUTC'],  # Use UTC time directly from the API
                            'date': today,
                            'gameId': game['id'],
                        }
                        create_game_file(game_details)

# Run the function to check games and create files
if __name__ == '__main__':
    check_and_create_game_files()
