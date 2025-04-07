# Flight Price Tracker

## Project Overview
This project is a Flight Price tracker that automates the process of collection and analyzing flight prices for set routes that I'm personally interested in. It pulls data from Google Flights daily and visualizes price trends over time to help identify the best time to book.

## Motivation
As someone who loves to travel, I wanted a data-driven way to monitor flight prices for destinations I want to travel to in the next couple years: Calgary, Lisbon, Madrid, and Tokyo (Narita) - all departing from Toronto. Instead of checking prices manually, I automated the entire process and added trend visualizations to support my decisions. 

## Tools & Technologies
- **Python:** Used to create the automation bot and data processing steps.
- **Selenium:** For scraping real-time prices from Google Flights.
- **PostgreSQL:** Database for storing flight data.
- **Power BI:** For building an interactive visualization.
- **Linux:** Server to host the PostgreSQL database and uses `cron` to automate daily data collection.

## Data Pipeline
1. **Scraping:** Selenium bot navigates to Google Flights and retrives the current lowest price for 4 specific routes with set departure and arrival dates.
2. **Cleaning:** Python parses and processes the data, converting it into a consistent format and ensuring datatypes are correct.
3. **Storage:** Data is uploaded to a PostgreSQL database, appending new records daily.
4. **Automation:** The entire script runs automatically every day at **5 AM** using `cron`.

## Visualization
I use Power BI to create four line charts - one for each route - showing how prices change over time.

You can see the visualization here: https://ankushonline.ca/pages/projects/flight-price-tracker.html

## Technical Details and Challenges
The main challenge faced was obtaining the data for this project. While I was familliar on how to create Selenium bots, the process of scraping the data through Google Flights was harder then antiicpated. Finding specific HTML tags for each data points of interest was not possible as there was no consistent identifier for them. I had to resort to extracting two strings, one for depature data and one for return data:

> From 311 Canadian dollars round trip total. Nonstop flight with Flair Airlines. Leaves Toronto Pearson International Airport at 2:55 PM on Friday, August 22 and arrives at Calgary International Airport at 5:10 PM on Friday, August 22. Total duration 4 hr 15 min.  Select flight

> From 311 Canadian dollars round trip total. Nonstop flight with Flair Airlines. Leaves Calgary International Airport at 1:55 PM on Tuesday, August 26 and arrives at Toronto Pearson International Airport at 7:50 PM on Tuesday, August 26. Total duration 3 hr 55 min.  Separate tickets. You'll buy each ticket in this itinerary separately. Select flight

I was able to parse these strings using **regex** to obtain the relevant details. Additionally, Google Flights lists the "best" flight as the very first option, which is the flight the bot scrapes. This is a limitation as it relies on Google's definition of "best", which may not match mine in some situations.

Aside from the data challenges, this is my first project using Power BI. My data visualization experience has been solely in Tableau within my professional career. It was a challenge to learn Power BI at the beginning, but I was able to leverage my Tableau knowledge to quickly learn and create this visualziation.
