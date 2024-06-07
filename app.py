from flask import Flask, render_template, make_response
import pandas as pd

app = Flask(__name__)

# Load datasets
airports_df = pd.read_excel('./database/airportcode.xlsx')
carriers_df = pd.read_excel('./database/carriercode.xlsx')

# Create a dictionary to store airport details by IATA code
airport_details = {row['IATACode']: row for index, row in airports_df.iterrows()}
airport_details2 = {row['country_code']: row for index, row in airports_df.iterrows()}

@app.route('/')
def index():
    # Convert dataframes to HTML
    airports_html = airports_df.to_html(classes='airports')
    carriers_html = carriers_df.to_html(classes='carriers')
    
    # Ensure that the 'country_code' is a string
    airports_df['country_code'] = airports_df['country_code'].astype(str)
    
    # Render index template with data
    return render_template('index.html', airports=airports_df.to_dict(orient='records'), airports_html=airports_html, carriers_html=carriers_html)

@app.route('/airports/<iata_code>')
def airport(iata_code):
    # Render a template for the specific airport using its IATA code
    if iata_code in airport_details:
        return render_template('airport.html', details=airport_details[iata_code])
    else:
        return "Airport not found", 404
    
@app.route('/flags/<country_code>')
def flag(country_code):
    # Serve flag images with proper cache control
    response = make_response(app.send_static_file(f'flags/{country_code.lower()}.svg'))
    response.cache_control.max_age = 86400  # Cache for 1 day
    return response


@app.route('/countries/<country_code>')
def get_airports_by_country(country_code):
    # Filter the dataframe by country code
    filtered_df = airports_df[airports_df['country_code'] == country_code]
    # Convert the filtered dataframe to a dictionary
    findf = filtered_df.to_dict(orient='records')
    # Render the 'country.html' template with the airports data
    return render_template('country.html', cntairports=findf)

@app.route('/continents/<continent>')
def get_airports_by_continent(continent):
    # Filter the dataframe by country code
    filtered_df = airports_df[airports_df['continent'] == continent]
    # Convert the filtered dataframe to a dictionary
    findf = filtered_df.to_dict(orient='records')
    # Render the 'country.html' template with the airports data
    return render_template('continent.html', cntairports=findf)

if __name__ == '__main__':
    app.run(debug=True)
