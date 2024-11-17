# game_monitor.py
import json
import time
import os
from datetime import datetime, timezone
import argparse
from player_lookup import create_player_id_to_player_dictionary
from game_monitor_utils import load_game_details, wait_until_game_start, fetch_play_by_play, get_number_of_api_calls

# Track and log each play event
def monitor_game(game_file, player_dict):
    game_details = load_game_details(game_file)
    game_id = game_details['game_id']
    start_time = game_details['start_time']
    # Wait until game start time
    current_time = datetime.now(timezone.utc)
    time_to_start = (start_time - current_time).total_seconds()
    targetEvents = {"game-start", "game-end", "period-start", "period-end", "goal","penalty"}
    
    if time_to_start > 0:
        print(f"Waiting {time_to_start} seconds until game start...")
        time.sleep(time_to_start)
    
    print("Game started. Beginning to monitor events.\n")
    print(f"{game_details['away_team']} at {game_details['home_team']} \n")
    last_sort_order = -1  # Initialize to a value that doesn't exist in 'sortOrder'


    while True:
        data = fetch_play_by_play(game_id)
        if data and "plays" in data:
            # Filter new events based on 'sortOrder'
            plays = data["plays"]
            new_plays = [play for play in plays if play["sortOrder"] > last_sort_order]
            
            if new_plays:
                # Sort new plays by 'sortOrder' for sequential logging
                new_plays.sort(key=lambda x: x["sortOrder"])
                
                # Log each new play to the file
                for play in new_plays:
                    play_type = play.get("typeDescKey", "unknown")
                    if play_type in targetEvents:
                        if play_type == "game-end":
                            log_play_event(game_file, play, player_dict)
                            print("Game ended. Stopping event log.\n")
                            total_number_of_api_calls = get_number_of_api_calls()
                            print(f"Total Number of API Calls: {total_number_of_api_calls}" )
                            return None
                        else:
                            log_play_event(game_file, play, player_dict)
                            last_sort_order = play["sortOrder"]

        time.sleep(10)  # Poll every 10 seconds

# Log individual play events to the game file
def log_play_event(game_file, play, player_dict):
    with open(game_file, 'a') as file:
        play_type = play.get("typeDescKey", "unknown")
        time_in_period = play.get("timeInPeriod", "unknown")
        period = play["periodDescriptor"].get("number", "unknown")
        team_id = play["details"].get("eventOwnerTeamId", "unknown") if "details" in play else "unknown"
        
        player_id = None
        if "details" in play and "scoringPlayerId" in play["details"]:
            player_id = play["details"]["scoringPlayerId"]
        
        if player_id and player_id in player_dict:
            player_name = player_dict[player_id]["lastName"]["default"]
        else:
            player_name = "Unknown Player"
     
        file.write(f"Period: {period}, Time in Period: {time_in_period} ")
        file.write(f"Event Type: {play_type} ")
        file.write(f"Team ID: {team_id} ")
        file.write(f"Player: {player_name} ")
        file.write("Details:\n")
        file.write(json.dumps(play, indent=2))  # Write the full play details in JSON format
        file.write("\n\n")
        print(f"Logged event: {play_type} in period {period}, time {time_in_period} by {player_name}")

# Main function to parse arguments and start monitoring
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Monitor NHL game events")
    parser.add_argument("game_file", type=str, help="Path to the game details file")
    args = parser.parse_args()
    
    game_details = load_game_details(args.game_file)
    start_time = game_details['start_time']
    game_id = game_details['game_id']
    
    print(f"Game Details: {game_details} TEST \n")
    
    # Fetch player dictionary
    player_dict = create_player_id_to_player_dictionary(game_id)
    if not player_dict:
        print("Failed to build player dictionary. Exiting.")
        exit(1)

    # Wait until the game starts before monitoring
    wait_until_game_start(start_time)
    
    # Call your monitor_game 
    monitor_game(args.game_file, player_dict)