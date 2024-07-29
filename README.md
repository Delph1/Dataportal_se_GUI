# Dataportal.se GUI

## Dataportal 

This app acts as a GUI for the Kolada API, which is referenced by [dataportal.se](www.dataportal.se). It serves over 6000 different KPIs that allows you to compare key index data of municipalities in Sweden. 

Anything from the quota of diesel cars to money spent on special needs education can be found through API. It's just that there is not GUI for it. You gotta locate the API first and second you have to query it, and after that you need to construct some form of comparison depending on the the data you got back. 

This App does all of that for you. You don't even need to go to datapportal.se, you can just use the app.

The app is written in Python using the FastAPI framework with some light JavaScript usage (select2 not the least) and utilizes an SQL database. I used MySQL. You can choose whatever you want by modifying the FastAPI settings.  

## Setup process

You first need to populate the KPI table by running, you guessed it, populate_kpis.py.

´´´
python populate_kpis.py
´´´

You then need to fetch the municipalities and inset them into the correct table by running:

´´´
python fetch_municipalities.py
´´´

You should now have a functional site at whatever node you have pointed the app to. 

A further development of the site would of course to make these steps included in the creation of the website or make the mandatory steps to run if the tables are not populated. 
