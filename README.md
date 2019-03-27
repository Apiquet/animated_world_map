# LINKS:

Github: https://github.com/Apiquet/animated_world_map

My website: https://anthonypiquet.wordpress.com/2018/12/04/displaying-data-on-an-animated-world-map/


# DESCRIPTION:

The objective was creating animated maps which displays the protests locations, frequency and kind (Engage in political dissent, Conduct strike or boycott, hunger strike, etc) 
day by day. This project asked me knowledge in Python and JavaScript, HTML/CSS.

First, I sent a query to **GDELT**'s event table to get all the protests they have. I got millions of rows with the date of each protest and its longitude/latitude. 

As you cannot send this query without a BigQuery Google account, I saved the data to csv files.

Then, I found a js script that display a moving marker on a map (from: https://github.com/ewoken/Leaflet.MovingMarker). I updated it to my wishes: marker's number dynamic, 
adding the location (latitude, longitude), adding a date attribute to each marker, changing the size of the markers in function of the number of markers in the same area, etc.

As everything is generic, I can update parameters like the number of markers, the speed, the location from global variables in the python script. 

I finally got animated maps with markers which draw each protest location in sequence with an updated date in the left corner.

Please open the **visualizing_main_maps.html** in 'animated_world_map\' to see the results.



# HOW TO RUN:

You may need to install packages:
	- branca
	- folium

Simply run: main.py

You can access some useful functions I have done in the functions folder.
