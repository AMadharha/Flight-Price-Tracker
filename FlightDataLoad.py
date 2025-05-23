from GoogleFlightBot import GoogleFlightBot
import re
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
import logging

def parse_flight_info(departure_str, return_str, flight_year):
    def parse_segment(segment, trip_type, trip_id):
        price_match = re.search(r'From ([\d,]+) (\w+) dollars', segment)
        stops_match = re.search(r'(\d+ stop|Nonstop)', segment)
        airline_match = re.search(r'flight with ([\w\s\-]+)\.', segment)
        dep_info_match = re.search(r'Leaves (.*?) at ([\d: APM]+) on (\w+), ([\w]+ \d+)', segment)
        arr_info_match = re.search(r'arrive[s]? at (.*?) at ([\d: APM]+) on (\w+), ([\w]+ \d+)', segment)
        duration_match = re.search(r'Total duration (.+?)\.', segment)

        # Extracted values
        price = int(price_match.group(1).replace(",", "")) if price_match else None
        currency = price_match.group(2) if price_match else None
        stops = 0 if 'Nonstop' in stops_match.group(1) else int(stops_match.group(1).split()[0]) if stops_match else None
        airline = airline_match.group(1).strip() if airline_match else None
        dep_airport = dep_info_match.group(1).strip() if dep_info_match else None
        dep_time = dep_info_match.group(2).replace('\u202f', ' ') if dep_info_match else None
        dep_date_raw = dep_info_match.group(4).strip() if dep_info_match else None
        arr_airport = arr_info_match.group(1).strip() if arr_info_match else None
        arr_time = arr_info_match.group(2).replace('\u202f', ' ') if arr_info_match else None
        arr_date_raw = arr_info_match.group(4).strip() if arr_info_match else None
        duration = duration_match.group(1).strip() if duration_match else None

        # Parse and format dates
        try:
            dep_date = datetime.strptime(f"{dep_date_raw} {flight_year}", "%B %d %Y").strftime("%Y-%m-%d")
            arr_date = datetime.strptime(f"{arr_date_raw} {flight_year}", "%B %d %Y").strftime("%Y-%m-%d")
        except:
            dep_date, arr_date = None, None

        # Return data
        row =  {
            'id': trip_id,
            'price': price,
            'currency': currency,
            'stops': stops,
            'airline': airline,
            'departure_airport': dep_airport,
            'departure_time': dep_time,
            'departure_date': dep_date,
            'arrival_airport': arr_airport,
            'arrival_time': arr_time,
            'arrival_date': arr_date,
            'duration': duration
        }

        if trip_type == 'return':
            return_row = {f"return_{key}": value for key, value in row.items() if key not in ['id']}
            return return_row
        
        return row

    trip_id = str(uuid.uuid4())  # Unique ID for the roundtrip
    dep_data = parse_segment(departure_str, 'departure', trip_id)
    ret_data = parse_segment(return_str, 'return', trip_id)

    # combine data
    combined_data = {**dep_data, **ret_data}

    df = pd.DataFrame([combined_data])

    return df
    
# Load environment variables
load_dotenv("/home/kush0/projects/Flight-Price-Tracker/.env")
#load_dotenv('./.env')

log_filename = f"{os.getenv("LOG_PATH")}flight_price_tracker_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logging.info("Script started.")

try:
    # Initialzie google flight bot
    gf_bot = GoogleFlightBot(os.getenv('CHROME_DRIVER_PATH'), headless=True)

    # Run the bot for different routes
    YYC = gf_bot.run(origin='YYZ', destination='YYC', departure_dt='2025-08-22', return_dt='2025-08-26')
    NRT = gf_bot.run(origin='YYZ', destination='NRT', departure_dt='2026-08-02', return_dt='2026-08-12')
    MAD = gf_bot.run(origin='YYZ', destination='MAD', departure_dt='2026-08-02', return_dt='2026-08-12')
    LIS = gf_bot.run(origin='YYZ', destination='LIS', departure_dt='2026-08-02', return_dt='2026-08-12')
    logging.info("Sucessfully pulled flight data.")

    # Extract flight details
    df_YYC = parse_flight_info(YYC[0], YYC[1], flight_year='2025')
    df_NRT = parse_flight_info(NRT[0], NRT[1], flight_year='2026')
    df_MAD = parse_flight_info(MAD[0], MAD[1], flight_year='2026')
    df_LIS = parse_flight_info(LIS[0], LIS[1], flight_year='2026')
    logging.info("Sucessfully parsed flight data.")

    all_flights_df = pd.concat([
        df_YYC,
        df_NRT,
        df_MAD,
        df_LIS
    ], ignore_index=True)

    # Add column for timestamp
    all_flights_df['created_at'] = datetime.today()

    # Convert datatypes
    all_flights_df['departure_date'] = pd.to_datetime(all_flights_df['departure_date'], errors='coerce').dt.date
    all_flights_df['arrival_date'] = pd.to_datetime(all_flights_df['arrival_date'], errors='coerce').dt.date
    all_flights_df['return_departure_date'] = pd.to_datetime(all_flights_df['return_departure_date'], errors='coerce').dt.date
    all_flights_df['return_arrival_date'] = pd.to_datetime(all_flights_df['return_arrival_date'], errors='coerce').dt.date

    all_flights_df['price'] = all_flights_df['price'].astype(int)
    all_flights_df['return_price'] = all_flights_df['return_price'].astype(int)

    all_flights_df['duration'] = all_flights_df['duration'].astype(str)
    all_flights_df['return_duration'] = all_flights_df['return_duration'].astype(str)
    all_flights_df['id'] = all_flights_df['id'].astype(str)
    all_flights_df['currency'] = all_flights_df['currency'].astype(str)
    all_flights_df['return_currency'] = all_flights_df['return_currency'].astype(str)
    all_flights_df['airline'] = all_flights_df['airline'].astype(str)
    all_flights_df['return_airline'] = all_flights_df['return_airline'].astype(str)
    all_flights_df['departure_airport'] = all_flights_df['departure_airport'].astype(str)
    all_flights_df['return_departure_airport'] = all_flights_df['return_departure_airport'].astype(str)
    all_flights_df['arrival_airport'] = all_flights_df['arrival_airport'].astype(str)
    all_flights_df['return_arrival_airport'] = all_flights_df['return_arrival_airport'].astype(str)
    logging.info("Successfully converted datatypes.")

    # connect to postgres
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_DATABASE')  

    connection_string = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'
    engine = create_engine(connection_string)

    # Upload dataframe to PostgreSQL
    all_flights_df.to_sql('flights', con=engine, if_exists='append', index=False)
    logging.info("Sucessfully uploaded data.")

    engine.dispose()

    with open(log_filename, 'a') as f:
        f.write("\n=== START OF DATA ===\n")
        f.write(all_flights_df.to_string(index=False))
        f.write("\n=== END OF DATA ===\n")

except Exception as e:
    logging.error("An error occurred", exc_info=True)