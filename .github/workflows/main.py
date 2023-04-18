import csv
import os
import requests
import uuid
import pandas as pd
import time



def get_filtered_streamers(language):
    start_time = time.time()
    root_dir = os.getcwd()

    print(f"Root-path: {root_dir}")
    
    
    

    # all_path = os.path.join(root_dir, "All.csv")
    all_path = os.getenv('ALL_URL')
    # only write the lang here to scrape and run code!!!!!!!
    Language = language

    # Replace with your Twitch API client ID and OAuth token
    CLIENT_ID = "dcmuk7wb06aro1cru1lz0ak8k2fs21"

    # tokens_path = os.path.join(root_dir, "tokens.txt")
    tokens_path = os.getenv('TOKENS_URL')

    with open(tokens_path) as f:
        access_token = f.readline().strip()
        refresh_token = f.readline().strip()

    print(f"Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    # Twitch app credentials
    client_id = 'dcmuk7wb06aro1cru1lz0ak8k2fs21'
    client_secret = 'wxggk34t8j3yho4mpy0ya8c5ue6i94'

    # Set up the Twitch API endpoint
    endpoint = 'https://api.twitch.tv/helix/users'

    # Set up the headers with the access token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-ID': client_id
    }

    # Validate the access token when the script starts
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 401:
        # The access token is invalid, so refresh it
        print('Access token is invalid, refreshing...')
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret
        }
        response = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, data=data)
        print(response.json())
        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data['access_token']
            refresh_token = response_data['refresh_token']
            print('Access token refreshed successfully!')
            print(f'New access token: {access_token}')
            print(f'New refresh token: {refresh_token}')
            # Update the file with new token values
            with open(tokens_path, "w") as f:
                f.write(access_token + "\n")
                f.write(refresh_token + "\n")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Client-ID': client_id
            }
            # Get the token expiration time and print it
            expires_in = response_data.get('expires_in')
            if expires_in:
                print(f'Token will expire in {expires_in / 60} minutes.')
            else:
                print('Token expiration time not found in response.')
            print(f'Token response: {response.content}')
        else:
            print('Access token could not be refreshed!')
            print(f'Status code: {response.status_code}')
            print(f'Response content: {response.content}')
            exit()
    else:
        # Get the token expiration time and print it
        expires_in = response.json().get('expires_in')
        if expires_in:
            print(f'Token will expire in {expires_in / 60} minutes.')
        else:
            print('Token expiration time not found in response.')

    # Get the user's information from the Twitch API
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        user_id = response_data['data'][0]['id']
        user_login = response_data['data'][0]['login']
        print(f'User ID: {user_id}')
        print(f'User login: {user_login}')
    else:
        print('Failed to get user information from Twitch API!')
        print(f'Status code: {response.status_code}')
        print(f'Response content: {response.content}')

    OAUTH_TOKEN = access_token

    En = 'en'
    Es = 'es'
    Pt = 'pt'



    if Language == Es:
        Input_Folder_Language = Es
    elif Language == Pt:
        Input_Folder_Language = Pt
    else:
        Input_Folder_Language = En


    # Twitch API endpoint for searching streams
    url = "https://api.twitch.tv/helix/streams"

    # Parameters for the API request
    params = {
        "first": 100, # Maximum number of results to retrieve per request (max 100)
        "language": Language, # Filter streams by language (optional)
        "type": "all", # Only retrieve live streams
    }

    # HTTP headers for the API request
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": "Bearer {}".format(OAUTH_TOKEN), # Include the OAuth token in the request
    }

    # Initialize variables for pagination
    streamers = []
    viewer_counts = []
    cursor = None
    total_results = 0

    # Make API requests to retrieve live streams until we have 100,000 results
    while total_results < 100000:
        # Set the "after" parameter to the cursor from the previous request
        if cursor:
            params["after"] = cursor

        # Send the API request and retrieve the response
        response = requests.get(url, params=params, headers=headers)

        # Check if the API request was successful
        if response.status_code != 200:
            raise Exception("Failed to retrieve streams: {}".format(response.text))

        # Parse the JSON data from the API response
        data = response.json()

        # Extract the streamers and viewer counts from the API response
        streamers += [stream["user_name"] for stream in data["data"]]
        viewer_counts += [stream["viewer_count"] for stream in data["data"]]
        total_results += len(data["data"])

        # Update the cursor for the next page of results
        cursor = data["pagination"].get("cursor")

        # Stop making API requests if there are no more results
        if not cursor:
            break

    # Save the list of streamers and viewer counts to merged_df

    fdata = []
    for i in range(len(streamers)):
        fdata.append([streamers[i], viewer_counts[i]])

    merged_df = pd.DataFrame(fdata, columns=["Streamer", "Viewer Count"]).astype(str)
    merged_df['Streamer'] = merged_df['Streamer'].str.lower()# Convert strings to lowercase

    # Print lan
    print(f'Filtering for language<" {Language} ">and updating All.csv with new streamers :')



    if Input_Folder_Language == En:
        Output_Path = os.getenv('EN_OUTPUT_URL')
        
        #Output_Path = os.path.join(root_dir, "en_output.csv")
    elif Input_Folder_Language == Es:
        
        Output_Path = os.getenv('ES_OUTPUT_URL')
        #Output_Path = os.path.join(root_dir, "es_output.csv")
    elif Input_Folder_Language == Pt:
        Output_Path = os.getenv('PT_OUTPUT_URL')
        #Output_Path = os.path.join(root_dir, "pt_output.csv")

    # Read All.csv
    all_df = pd.read_csv(all_path, dtype=str)

    # Read output file to append new results
    output_df = pd.read_csv(Output_Path, dtype=str)


    all_df.drop_duplicates(subset=['Streamer'], inplace=True) # Drop duplicates

    # Print number of rows in All.csv
    print(f'Number of rows in All.csv: {len(all_df)}')

    # Print number of rows in m.csv before removing duplicates
    print(f'Number of streamers scrapped live for this lang: {Language} : before removing duplicates: {len(merged_df)}')


    merged_df.drop_duplicates(subset=['Streamer'], inplace=True) # Drop duplicates

    # Print number of rows from api after removing duplicates
    print(f'Number of streamers scrapped live for this lang: {Language} : after removing duplicates: {len(merged_df)}')

    # Get the values in the first column of "All.csv"
    all_col = all_df.iloc[:, 0]



    merged_for_filter_df = pd.merge(merged_df, all_col, on="Streamer", how="inner")
    filtered_df = merged_df[~merged_df["Streamer"].isin(merged_for_filter_df["Streamer"])]
    filtered_df = filtered_df.reset_index(drop=True)
    # Print number of rows in filtered.csv
    print(f'Number of rows in filtered names for {Language}: {len(filtered_df)}')


    output_df = pd.concat([output_df, filtered_df])
    output_df = output_df.reset_index(drop=True)

    all_df = pd.concat([all_df, filtered_df])
    all_df = all_df.reset_index(drop=True)

    output_df.to_csv(Output_Path, index=False)


    # remove duplicates of All.csv

    all_df.drop_duplicates(subset=['Streamer'], inplace=True) # Drop duplicates

    # Save the updated All.csv file in the same directory as before, overwriting the old file
    all_df.to_csv(all_path, index=False)

    # Print number of rows in updated All.csv
    print(f'Number of rows in updated All.csv: {len(all_df)}')

    print(f'Output filtered results are in this folder : {Output_Path}')

    # Print time taken to run code
    print(f'Time taken to run code: {time.time() - start_time:.2f} seconds')

def main():

    get_filtered_streamers('pt')
    #get_filtered_streamers('es')
    #get_filtered_streamers('en')
    #get_filtered_streamers('de')
    #get_filtered_streamers('ru')
    #get_filtered_streamers('fr')
    #get_filtered_streamers('it')

if __name__ == '__main__':
    main()
