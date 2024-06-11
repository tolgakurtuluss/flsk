from flask import Flask, render_template, make_response, send_from_directory
import pandas as pd
from duckduckgo_search import DDGS

app = Flask(__name__)

# Load datasets
airports_df = pd.read_excel('./database/airportcode.xlsx')
carriers_df = pd.read_excel('./database/carriercode.xlsx')

# Ensure that the 'country_code' is a string
airports_df['country_code'] = airports_df['country_code'].astype(str)

# Create dictionaries to store airport details
airport_details = airports_df.set_index('IATACode').T.to_dict()
airport_details_by_country = airports_df.set_index('country_code').T.to_dict()

@app.route('/')
def index():
    # Example featured data
    featured_airports = airports_df.sample(8).to_dict(orient='records')
    featured_carriers = carriers_df.sample(8).to_dict(orient='records')
    popular_routes = [
        {'origin': 'JFK', 'destination': 'LAX', 'carrier_name': 'American Airlines'},
        {'origin': 'LHR', 'destination': 'CDG', 'carrier_name': 'British Airways'},
        {'origin': 'HND', 'destination': 'SFO', 'carrier_name': 'Japan Airlines'},
        {'origin': 'DXB', 'destination': 'SYD', 'carrier_name': 'Emirates'}
    ]

    return render_template('index.html', featured_airports=featured_airports, featured_carriers=featured_carriers, popular_routes=popular_routes)

@app.route('/airports/<iata_code>')
def airport(iata_code):
    # Render a template for the specific airport using its IATA code
    if iata_code in airport_details:
        
        video_id = get_first_video_id(iata_code)
        skyscanner_url = flights_from(iata_code)[0]
        kayak_url = flights_from(iata_code)[1]

        return render_template('airport.html', details=airport_details[iata_code], video_id=video_id, skyscanner_url=skyscanner_url, kayak_url=kayak_url)
    else:
        return "Airport not found", 404

@app.route('/flags/<country_code>')
def flag(country_code):
    # Serve flag images with proper cache control
    return send_from_directory('static/flags', f'{country_code.lower()}.svg', cache_timeout=86400)

@app.route('/countries/<country_code>')
def get_airports_by_country(country_code):
    # Filter the dataframe by country code
    filtered_df = airports_df[airports_df['country_code'] == country_code]
    # Convert the filtered dataframe to a dictionary
    airports_by_country = filtered_df.to_dict(orient='records')
    # Render the 'country.html' template with the airports data
    return render_template('country.html', cntairports=airports_by_country)

@app.route('/continents/<continent>')
def get_airports_by_continent(continent):
    # Filter the dataframe by continent
    filtered_df = airports_df[airports_df['continent'] == continent]
    # Convert the filtered dataframe to a dictionary
    airports_by_continent = filtered_df.to_dict(orient='records')
    # Render the 'continent.html' template with the airports data
    return render_template('continent.html', cntairports=airports_by_continent)

@app.route('/airports')
def airports():
    # Get list of airlines
    return render_template('aairports.html', airports=airports_df.to_dict(orient='records'), airports_html= airports_df.to_html(classes='airports'))

@app.route('/countries')
def countries():
    # Get list of airlines
    return render_template('ccountries.html', airports=airports_df.to_dict(orient='records'), airports_html= airports_df.to_html(classes='airports'))

def get_first_video_id(iata_code):
    search_query = f"{iata_code} airport live takeoff/landing intitle:{iata_code} insite:youtube.com/watch?v"
    results = DDGS().text(search_query, max_results=5)

    # Assuming the first result is a YouTube video, extract the video ID from the URL
    video_url = results[0]['href']
    video_id = video_url.split('v=')[1]
    
    return video_id

def flights_from(iata_code):
    # Construct the Skyscanner URL with the dynamic airport code
    skyscanner_url = f"https://www.skyscanner.com/flights-from/{iata_code}/"
    kayak_url = f"https://www.kayak.com/explore/{iata_code}-anywhere"
    return skyscanner_url, kayak_url

if __name__ == '__main__':
    app.run(debug=True)
