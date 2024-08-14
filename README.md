# Vacation Planner

This project is a web application you can use to plan a vacation to the most popular tourist destinations in the US and across the world! 
1. Input your preferred destination from a list of over 300 cities worldwide.
2. Choose an itinerary of activities from a list of popular things to do in your chosen city.
3. Recieve an optimized and adjustable schedule of daily routes through your chosen activities for your vacation.
  
This README file will contain:
 -  A brief overview of how this application works and the programming behind it.
 -  Instructions to run this application on your own machine.
 -  A video demo.  

## How Vacation Planner Works

This web application is a fullstack software engineering project with focus on front-end design in HTML, webscraping techniques in Python, and algorithmic programming with graph theory. Here is a little bit about what I did to put this project together...
* How it works:
  * This application webscrapes https://travel.usnews.com/ for data on a user-chosen city.
  * With this application's intuitive and interactive HTML web service, the user has full control over chosing activities to add to their itinerary.
  * This project's python algorithms utilize the google maps API to plan an optimal route through all user-chosen activites.
  * The application then autonomously provides an optimal and informative schedule for the user's vacation allowing for user adjustment.

## Skills I Learned

  * Webscraping in Python
  * HTML + CSS + JS web design
  * Implementing greedy algorithms + applications in graph theory
  * Utilizing the google maps API
  * Flask + jinja framework

## Run Instructions

In order to run this application you must have the following:
* Python >= 3.10
* [Poetry](https://python-poetry.org)
* [Google Maps API Key](https://developers.google.com/maps/documentation/embed/get-api-key)

Once you have this repository cloned, run the following commands in a terminal at thh root of the directory:

1. Save you Google Maps API key as an environment variable  
  
For macOS:
```bash
export GMAPS_API_KEY=YourSecretKey
```
For Windows:
```bash
set GMAPS_API_KEY=YourSecretKey
```
2. Install dependencies
```bash
poetry install
```
3. Run Flask web applicaiton
```bash
poetry run python run_flask.py
```
  
## DEMO

Coming soon...
