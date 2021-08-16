# mhdcrime
## About 

[mhdcrime.org](https://mhdcrime.org) is a map of police activity in the town of Marblehead, MA. It offers an interactive display of the data provided by the Marblehead Police Department's [daily logs](https://www.marblehead.org/police-department/pages/daily-log-2021)

## How does it work?

Logs from [marblehead.org](marblehead.org) are downloaded and scraped every 24 hours. Logs are then split up into "reports", designated by a unique call number provided by the police derpartment.

Each report is then added to a database with a geocoded location and plotted onto a map

## Features 

- A comprehensive map of all reported incidents in the town of Marblehead dating back to 2019, comlete with search functionality and filters. 
- A live community map with the ability to create, edit, and remove user provided reports, complete with local police & fire dispatch feed

## Setup 

### Requirements 

~~~
pip install -r requirements.txt
~~~


- This project requires a modified version of flask-googlemaps found [here](https://github.com/getcake/Flask-GoogleMaps-mhdcrime)
    - 
    ~~~
        git clone https://github.com/getcake/Flask-GoogleMaps-mhdcrime
        pip install Flask-GoogleMaps-mhdcrime/
    ~~~

- In order to create and populate the databse, uncomment the scheduler code found in run.py 
    - This may take a long time and is not recommended for those with a slow connection 

- Modify the directories in the following files to suit your environment

~~~
main.py

get_reports.py
~~~


- Register a google maps [api key](https://developers.google.com/maps/documentation/javascript/get-api-key)

  - set your key in views.py 
  -  ~~~
     GoogleMaps(server, key="ENTER_KEY")
      ~~~


## Due Credit  

Thanks to [Creative Tim](https://www.creative-tim.com/product/soft-ui-dashboard) for his awesome bootstrap template! 
