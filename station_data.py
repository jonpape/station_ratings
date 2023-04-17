import os
import pandas as pd
import polars as pl
import googlemaps
from googlemaps.exceptions import ApiError
from dotenv import load_dotenv
import os

# List all CSV files in the trade_prices directory
csv_files = [file for file in os.listdir('archive/trade_prices') if file.endswith('.csv')]

# Initialize an empty DataFrame
data = pd.DataFrame()

# Load each CSV file into a DataFrame and concatenate them
for file in csv_files:
    file_path = os.path.join('archive/trade_prices', file)
    # temp_data = pl.read_csv(file_path).to_pandas()
    temp_data = pd.read_csv(file_path, dtype={'Renovation': str, 'Purpose': str, 'FloorPlan': str})
    data = pd.concat([data, temp_data], ignore_index=True)

print(data.head())

station = data['NearestStation'].unique()

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
api_key = os.getenv('API_KEY')

gmaps = googlemaps.Client(key=api_key)

ratings = {}

for s in station:
    if s == 'None':
        continue
    if isinstance(s, (int, float)):
        continue

    # Define the name of the place you want to retrieve reviews for
    place_name = s

    # Search for the place using its name and retrieve its details
    places = gmaps.places(place_name + " station japan")

    if(len(places['results']) == 0):
        continue

    # Extract the place ID from the search results
    place_id = places['results'][0]['place_id']

    # Retrieve the reviews for the specified place
    #place_details = gmaps.place(place_id, fields=['rating'])

    try:
        # Try to get details for the place ID
        place_details = gmaps.place(place_id, fields=['rating'])
        if 'rating' in place_details['result']:
            rating = place_details['result']['rating']
            print(f"The rating for {s} is {rating}")
            ratings[s]=rating

    except ApiError as e:
        if 'NOT_FOUND' in str(e.args):
            # Ignore the error and continue with your code
            pass
        else:
            # Handle other API errors
            print(f'Error getting place details: {e}')


# Write the DataFrame to the output CSV file
df = pd.DataFrame(list(ratings.items()), columns=['station', 'rating'])

# Write the DataFrame to the output CSV file
df.to_csv('station_data.csv', index=False)
