# game_monitor.py
import json
import time
import os
from datetime import datetime, timezone
import argparse
from player_lookup import create_player_id_to_player_dictionary
from game_monitor_utils import load_game_details, wait_until_game_start, fetch_play_by_play, get_number_of_api_calls
from game_event_handler import handle_game_events

# Track and log each play event
def monitor_game(game_file, player_dict, game_details):
    game_id = game_details['game_id']
    start_time = game_details['start_time']
    # Wait until game start time
    current_time = datetime.now(timezone.utc)
    time_to_start = (start_time - current_time).total_seconds()
    target_events = {"game-start", "game-end", "period-start", "period-end", "goal","penalty"}
    
    if time_to_start > 0:
        print(f"Waiting {time_to_start} seconds until game start...")
        time.sleep(time_to_start)
    
    print("Game started. Beginning to monitor events.\n")
    print(f"{game_details['away_team']} at {game_details['home_team']} \n")
    last_sort_order = -1  # Initialize to a value that doesn't exist in 'sortOrder'
    handle_game_events(game_id, target_events)
""""
    while True:
        data = fetch_play_by_play(game_id)
        if data and "plays" in data:
            # Filter new events based on 'sortOrder'
            events = data["plays"]
            new_events = [event for event in events if event["sortOrder"] > last_sort_order]
            
            if new_events:
                # Sort new plays by 'sortOrder' for sequential logging
                new_events.sort(key=lambda x: x["sortOrder"])
                
                # Log each new play to the file
                for event in new_events:
                    event_type = event.get("typeDescKey", "unknown")
                    if event_type in targetEvents:
                        if event_type == "game-end":
                            log_play_event(game_file, event, player_dict)
                            print("Game ended. Stopping event log.\n")
                            total_number_of_api_calls = get_number_of_api_calls()
                            print(f"Total Number of API Calls: {total_number_of_api_calls}" )
                            return None
                        else:
                            log_play_event(game_file, event, player_dict)
                            last_sort_order = event["sortOrder"]

        time.sleep(10)  # Poll every 10 seconds
"""
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
    
    # print(f"Game Details: {game_details} TEST \n")
    
    # Fetch player dictionary
    player_dict = create_player_id_to_player_dictionary(game_id)
    if not player_dict:
        print("Failed to build player dictionary. Exiting.")
        exit(1)

    # Wait until the game starts before monitoring
    wait_until_game_start(start_time)
    
    # Call your monitor_game 
    monitor_game(args.game_file, player_dict, game_details)
