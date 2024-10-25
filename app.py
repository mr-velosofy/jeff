from flask import Flask, request
import re
import time
import requests
import os
from dotmap import DotMap

app = Flask(__name__)

def parse_time_string(time_string):
    time_in_seconds = 0
    time_units = {"hour": 3600, "hours": 3600, "minute": 60, "minutes": 60, "second": 1, "seconds": 1}
    
    # Extract numbers and units from the time string
    matches = re.findall(r'(\d+)\s*([a-zA-Z]+)', time_string)
    
    for number, unit in matches:
        if unit in time_units:
            time_in_seconds += int(number) * time_units[unit]
        else:
            raise ValueError(f"Unknown time unit: {unit}")
    
    return time_in_seconds

def ttv_start_time(query):
    try:
        total_seconds = parse_time_string(query)
        current_time_unix = int(time.time())
        start_time_unix = current_time_unix - total_seconds
        return start_time_unix
    except Exception as e:
        print("An error occurred while calculating start time:", str(e))
        return None

@app.route("/record/nightbot/<streamer>/<region>/<id>/<tag>/<time>")
def record_nightbot(streamer, region, id, tag, time):
    header = {'Authorization': os.getenv("hdev_key")}
    
    if "not" in time:
        return f"{streamer} is not live"
      
    else:
        start_time = ttv_start_time(time)
        stream_start = int(start_time)
    
    win = 0
    draw = 0
    lose = 0
    
    mmrhistory_url = f"https://api.henrikdev.xyz/valorant/v1/mmr-history/{region}/{id}/{tag}"
    # Fetch JSON data from the external URL
    mmrhistory_data = requests.get(mmrhistory_url, headers=header)
    response_message = ""
    
    if mmrhistory_data.status_code == 200:
        # Parse JSON data
        mmrhistory_json = mmrhistory_data.json()
        mmrhistory_dotmap = DotMap(mmrhistory_json)
        total_mmr_change = 0
        print(stream_start)
        # Iterate over the data list
        for data in mmrhistory_dotmap.data:
            match_start = data.date_raw
            
            if match_start > stream_start:
                total_mmr_change += data.mmr_change_to_last_game

                # Check the MMR change to determine the outcome
                if data.mmr_change_to_last_game == -3:
                    pass
                elif -5 <= data.mmr_change_to_last_game <= 5:
                    draw += 1
                elif data.mmr_change_to_last_game > 5:
                    win += 1
                elif data.mmr_change_to_last_game < -5:
                    lose += 1
                    
            else:
                break
                    
        up_or_down = "UP" if total_mmr_change >= 0 else "DOWN"
        total_mmr_change = abs(total_mmr_change)
        
        if win + lose + draw == 0:
            response_message = f"{streamer} has not finished any competitive match yet."
        else:
            response_message = f"{streamer} is {up_or_down} {total_mmr_change} RR, with {win} wins, {lose} losses, and {draw} draws this stream."
    
    else:
        response_message = "Riot API seems to be down"

    return response_message

@app.route("/record/fossabot/<streamer>/<region>/<id>/<tag>/<time>")
def record_fossabot(streamer, region, id, tag, time):
    header = {'Authorization': os.getenv("hdev_key")}
    
    if "offline" in time.lower():
        return f"{streamer} is not live"
      
    else:
        start_time = ttv_start_time(time)
        stream_start = int(start_time)
    
    win = 0
    draw = 0
    lose = 0
    
    mmrhistory_url = f"https://api.henrikdev.xyz/valorant/v1/mmr-history/{region}/{id}/{tag}"
    # Fetch JSON data from the external URL
    mmrhistory_data = requests.get(mmrhistory_url, headers=header)
    response_message = ""
    
    if mmrhistory_data.status_code == 200:
        # Parse JSON data
        mmrhistory_json = mmrhistory_data.json()
        mmrhistory_dotmap = DotMap(mmrhistory_json)
        total_mmr_change = 0
        print(stream_start)
        # Iterate over the data list
        for data in mmrhistory_dotmap.data:
            match_start = data.date_raw
            
            if match_start > stream_start:
                total_mmr_change += data.mmr_change_to_last_game

                # Check the MMR change to determine the outcome
                if data.mmr_change_to_last_game == -3:
                    pass
                elif -5 <= data.mmr_change_to_last_game <= 5:
                    draw += 1
                elif data.mmr_change_to_last_game > 5:
                    win += 1
                elif data.mmr_change_to_last_game < -5:
                    lose += 1
                    
            else:
                break
                    
        up_or_down = "UP" if total_mmr_change >= 0 else "DOWN"
        total_mmr_change = abs(total_mmr_change)
        
        if win + lose + draw == 0:
            response_message = f"{streamer} has not finished any competitive match yet."
        else:
            response_message = f"{streamer} is {up_or_down} {total_mmr_change} RR, with {win} wins, {lose} losses, and {draw} draws this stream."
    
    else:
        response_message = "Riot API seems to be down"

    return response_message


if __name__ == "__main__":
    app.run(debug=True,port=5000)