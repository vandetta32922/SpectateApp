import lcu_driver
import os

# Initialize LCU driver
connector = lcu_driver.Connector()

@connector.ready
async def connect(connection):
    # Read the game name and tag from player.txt
    folder_path = "."
    with open(os.path.join(folder_path, 'player.txt'), 'r') as file:
        player_info = file.read().strip()
    
    # Encode the game name and tag for the URL
    player_info_url = player_info.replace('#', '%23')
    
    # Send GET request to LCU for summoner info
    response = await connection.request('get', f'/lol-summoner/v1/summoners?name={player_info_url}')
    
    if response.status == 200:
        data = await response.json()
        puuid = data.get("puuid")
        if puuid:
            print(f"PUUID: {puuid}")
            
            # Now, make the POST request to launch spectate
            spectate_data = {
                "dropInSpectateGameId": "SEX SEX SEX",
                "gameQueueType": "SEXXXXXX",
                "allowObserveMode": "ALL",
                "puuid": puuid
            }

            spectate_response = await connection.request(
                'post', 
                '/lol-spectator/v1/spectate/launch', 
                json=spectate_data
            )

            if spectate_response.status == 200:
                print("Spectate request successful.")
            else:
                print(f"Spectate request failed with status code {spectate_response.status}")
        else:
            print("PUUID not found.")
    else:
        print(f"Request failed with status code {response.status}")

# Start the connector
connector.start()
