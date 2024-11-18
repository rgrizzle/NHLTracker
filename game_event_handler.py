# game_event_handler.py
import time
from game_monitor_utils import fetch_play_by_play
from player_lookup import create_player_id_to_player_dictionary

class GameEvent: 
    def __init__(self, event_id, event_type, period, period_type, time_in_period, time_remaining):
        self.event_id = event_id
        self.event_type = event_type
        self.period = period
        self.period_type = period_type
        self.time_in_period = time_in_period
        self.time_remaining = time_remaining
        
    def update_event(self, event_type=None, period=None, time_in_period=None, player=None):
        """Method to update existing event data."""
        if event_type:
            self.event_type = event_type
        if period:
            self.period = period
        if time_in_period:
            self.time_in_period = time_in_period
        if player:
            self.player = player
            
# Period Start or Stop GameEvent Subclass
class PeriodEvent(GameEvent):
    def __init__(self, event_id, event_type, period, time_in_period, time_remaining, period_type):
        super().__init__(event_id, event_type, period, time_in_period, time_remaining, period_type)

class GoalEvent(GameEvent):
    def __init__(self, event_id, event_type, period, period_type, time_in_period, time_remaining,
                 shot_type, scoring_player_id, scoring_player_name, scoring_player_goal_total, 
                 scoring_team_id, scoring_team_name, assist_one_player_id, assist_one_player_name, 
                 assist_one_player_assist_total, goalie_in_net_id, goalie_in_net_name):
        super().__init__(event_id, event_type, period, period_type, time_in_period, time_remaining)
        self.shot_type = shot_type
        self.scoring_player_id = scoring_player_id
        self.scoring_player_name = scoring_player_name
        self.scoring_player_goal_total = scoring_player_goal_total
        self.scoring_team_id = scoring_team_id
        self.scoring_team_name = scoring_team_name
        self.assist_one_player_id = assist_one_player_id
        self.assist_one_player_name = assist_one_player_name
        self.assist_one_player_assist_total = assist_one_player_assist_total
        self.goalie_in_net_id = goalie_in_net_id
        self.goalie_in_net_name = goalie_in_net_name

        
game_events = dict()

def handle_game_events(game_id, target_events):
    last_sort_order = -1  # Initialize to a value that doesn't exist in 'sortOrder'
    player_dict = create_player_id_to_player_dictionary(game_id)

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
                    event_id = event.get("eventId", "unkown")
                    event_type = event.get("typeDescKey", "unkown")
                    #print(f"event type: {event_type}")
                    
                    if event_type in target_events:
                        if event_type == "game-end" :
                            handle_game_end(event_id, event)
                            #print(game_events)
                            return
                        elif event_type == "period-start":
                            handle_period_start(event_id,event)
                        elif event_type == "period-end":
                            handle_period_end(event_id,event)
                        elif event_type== "goal":
                            handle_goal(event_id,event, player_dict)
                            
        time.sleep(10)  # Poll every 10 seconds
        
def handle_period_start(event_id, event):
    if event_id not in game_events:
        new_game_event = PeriodEvent(
            event_id = event_id,
            event_type = "Period Start",
            period = event["periodDescriptor"].get("number", "unknown"),
            period_type = event['periodDescriptor']['periodType'],
            time_in_period = event.get("timeInPeriod", "unknown"),
            time_remaining = event.get("timeRemaining", "unknown")
        )
        game_events[event_id] = new_game_event
        pnum = event['periodDescriptor']['number']
        ptype = event['periodDescriptor']['periodType']

        period_name = period_display_name(pnum, ptype)
        print(f" ### {period_name} START ###")

        
def handle_period_end(event_id, event):
    if event_id not in game_events:
        new_game_event = PeriodEvent(
            event_id = event_id,
            event_type = "Period End",
            period = event["periodDescriptor"].get("number", "unknown"),
            period_type = event['periodDescriptor']['periodType'],
            time_in_period = event.get("timeInPeriod", "unknown"),
            time_remaining = event.get("timeRemaining", "unknown")
        )
        game_events[event_id] = new_game_event
        pnum = event['periodDescriptor']['number']
        ptype = event['periodDescriptor']['periodType']

        period_name = period_display_name(pnum, ptype)
        print(f" ### {period_name}  END ###\n")
        
def handle_game_end(event_id, event):
        print(f"Game End\n")
        
        
def period_display_name(period, period_type):
    if period_type == 'REG':
        if period <= 3:
            return f"Period {period}"
    elif period_type == 'OT':
        return "Overtime"
    elif period_type == 'SO':
        return "Shootout"
    return None  # Default for unknown period types

def handle_goal(event_id, event, player_dict):
    if event_id not in game_events:
        #print(event["details"].get("assist1PlayerId"))
        #print(event["details"])
        if "scoringPlayerId" in event["details"]:
            scoring_player_id = event["details"].get("scoringPlayerId")
        else:
            scoring_player_id = None

        if "assist1PlayerId" in event["details"]:
            assist_one_player_id = event["details"].get("assist1PlayerId")
        else:
            assist_one_player_id = None

        if "goalieInNetId" in event["details"]:
            goalie_in_net_id = event["details"].get("goalieInNetId")
        else:
            goalie_in_net_id = None


        # Initialize variables with default values, will be conditionally updated later
        scoring_player_name = "Unknown Player"
        assist_one_player_name = "Unknown Player"
        goalie_in_net_name = "Unknown Player"
        scoring_player_goal_total = "unknown"
        assist_one_player_assist_total = "unknown"
        scoring_team_name = "Team Name"  # Placeholder for scoring team name

        # Assign values conditionally
        if scoring_player_id:
            #print(f"Looking Up Scoring Player for Id: {scoring_player_id}")
            scoring_player_name = player_dict.get(scoring_player_id, {}).get("lastName", "Unknown").get("default", "Unknown")
            scoring_player_goal_total = event["details"].get("scoringPlayerTotal", "unknown")
        
        if assist_one_player_id:
            #print(f"Looking Up A1 Player for Id: {scoring_player_id}")
            assist_one_player_name = player_dict.get(assist_one_player_id, {}).get("lastName", "Unknown").get("default", "Unknown")
            assist_one_player_assist_total = event["details"].get("assist1PlayerTotal", "unknown")

        if goalie_in_net_id:
            goalie_in_net_name = player_dict.get(goalie_in_net_id, {}).get("lastName", "Unknown")

        # Create the GoalEvent object with the assigned variabless
        new_game_event = GoalEvent(
            event_id = event_id,
            event_type = "Goal",
            period = event["periodDescriptor"].get("number", "unknown"),
            period_type = event["periodDescriptor"].get("periodType", "unknown"),
            time_in_period = event.get("timeInPeriod", "unknown"),
            time_remaining = event.get("timeRemaining", "unknown"),
            shot_type = event["details"].get("shotType", "unknown"),
            scoring_player_id = scoring_player_id, 
            scoring_player_name = scoring_player_name, 
            scoring_player_goal_total = scoring_player_goal_total, 
            scoring_team_id = event["details"].get("eventOwnerTeamId", "unknown"), 
            scoring_team_name = scoring_team_name, 
            assist_one_player_id = assist_one_player_id, 
            assist_one_player_name = assist_one_player_name, 
            assist_one_player_assist_total = assist_one_player_assist_total,
            goalie_in_net_id = goalie_in_net_id, 
            goalie_in_net_name = goalie_in_net_name
        )
        game_events[event_id] = new_game_event
        #print(f"a1 player Id: {new_game_event.assist_one_player_id}")
        print(f"{new_game_event.time_in_period} Goal Scored by {new_game_event.scoring_player_name} ({new_game_event.scoring_player_goal_total}), {new_game_event.assist_one_player_name} ({new_game_event.assist_one_player_assist_total})")
