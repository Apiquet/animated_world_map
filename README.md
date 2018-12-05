# animated_world_map

The objective was creating an animated world map which displays the protests locations day by day

First, I sent a query to **GDELT**'s event table to get all the protests they have. I got millions of rows with the date of each protest and its longitude/latitude. 

Then, I updated a js script with **the number of markers** I want, the **location** and **date** of each protest and a **move's speed** for the markers. 

As everything is generic, I can update the number of markers and the speed from a global variable in the python code. 

I finally got a world map with markers which draw each protest location in sequence thanks to the MovingMarker script (from: https://github.com/ewoken/Leaflet.MovingMarker) that I had to adapt to my needs.

Please open the **index.html** in  'Leaflet.MovingMarker-master\animated_map\' to see the result.
