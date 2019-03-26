
# coding: utf-8

# In[7]:


from google.cloud import bigquery
import pandas as pd
import numpy as np
import os
import json
import folium
import matplotlib.pyplot as plt
import matplotlib as mpl
from IPython.core.display import display, HTML
from IPython.core.display import Image, display

from sklearn.linear_model import LinearRegression, LogisticRegression
from branca.colormap import linear
import statsmodels.api as sm
from scipy import stats
from functions.folium_functions import *
from functions.dataframe_functions import *
from functions.getting_tables import *
from functions.animated_maps_functions import *
from functions.stats_functions import *

import seaborn as sns
from math import pi


DATA_PATH = "data/"
VISUALIZATION_PATH = "visualizations/"

FOLIUM_MAPS_PATH = VISUALIZATION_PATH + "folium_maps/"
STATS_REGION_PATH = VISUALIZATION_PATH + 'stats_regions/'
ANIMATED_MAP_PATH = VISUALIZATION_PATH +  'animated_maps/'

WORLD_MAP_TYPE_PATH = ANIMATED_MAP_PATH + 'world_map_type/'
WORLD_MAP_FREQ_PATH = ANIMATED_MAP_PATH + 'world_map_freq/'
COUNTRY_MAP_PATH = ANIMATED_MAP_PATH + 'individual_country_map/'
US_MAP_PATH = ANIMATED_MAP_PATH + 'us_map_elections/'
US_MAP_FREQ_PATH = ANIMATED_MAP_PATH + 'us_map_freq/'
GDP_GROWTH_STAT_PATH = VISUALIZATION_PATH + 'GPD_Growth_protests_count/'

# Using of BigQuery to load data from GDELT
# In comment because it needs a google big query account
# I saved all the data in csv file available in the data folder

#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\antho\\Downloads\\adafinalproject-b2214ea058a4.json'
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\bot_\\Downloads\\AdaProject-3323118f7315.json'
# get json by following (Setting up authentication)
# https://cloud.google.com/bigquery/docs/reference/libraries

#bigquery_client = bigquery.Client()


# # Getting the main tables:
# 
# - event codes table
# - indication of richness per inhabitant per country
# - Protests for leadership change
# - Protests for rights
# - country codes table
# - country codes conversion iso2 to iso3
# - statistics on countries

# ### Event codes:

event_codes = pd.read_csv(DATA_PATH + "eventcodes.csv", encoding = "ISO-8859-1")


# ### Indication of richness per inhabitant per country per year:

country_by_income_per_year = pd.read_csv(DATA_PATH + "country_by_income.csv", encoding = "ISO-8859-1")


#here we only get an indicator of the income, we need to transform it to process it
#we choose to transform Low income (L) to -3, (LM) to -1, (UM) to 1, (H) to 3
country_by_income_per_year=convert_income_to_numerical(country_by_income_per_year)


# ### Getting all protests events:
# With:
# - ##### <u> ID </u>
# - ##### <u> CountryCode </u>
# - ##### <u> EventCode </u>
# - ##### <u> Year </u>


reload = False
if os.path.isfile(DATA_PATH + 'protests_df_raw_1.csv') and os.path.isfile(DATA_PATH + 'protests_df_raw_2.csv') and not reload :
    protests_df_raw_1 = pd.read_csv(DATA_PATH + 'protests_df_raw_1.csv')
    protests_df_raw_2 = pd.read_csv(DATA_PATH + 'protests_df_raw_2.csv')
    
else:
    query_protests = bigquery_client.query(
        """SELECT GLOBALEVENTID as ID, ActionGeo_CountryCode as CountryCode,  EventCode,MonthYear,NumMentions,AvgTone, Year FROM `gdelt-bq.gdeltv2.events` 
        WHERE EventCode LIKE '14%' """)
    protests_df_raw = query_protests.result().to_dataframe()
    # Write down the csv
    protests_df_raw_1 = protests_df_raw[0:int(np.floor(len(protests_df_raw)/2))]
    protests_df_raw_2 = protests_df_raw.iloc[int(np.floor(len(protests_df_raw)/2)):,]
    
    protests_df_raw_1.to_csv(DATA_PATH + 'protests_df_raw_1.csv', index=False)
    protests_df_raw_2.to_csv(DATA_PATH + 'protests_df_raw_2.csv', index=False)

protests_df_raw = pd.concat([protests_df_raw_1, protests_df_raw_2], ignore_index=True)    
protests_df = protests_df_raw.dropna()


# ### Country codes conversion between :
# - fips104,  iso2 and iso3
# - iso3 and name:

country_codes_to_name,country_codes_fips104_to_iso3= load_countrycode(DATA_PATH)
#join the protests dataframe to get the iso3 convention for each country
protests_df=pd.merge(protests_df, country_codes_fips104_to_iso3, how='right', left_on=['CountryCode'], right_on=['FIPS 10-4'])
#changing the column name to keep the same naming convention in each dataframe
protests_df = protests_df.dropna()


# ### Getting statistics on countries:

#Getting data about statistics on all the countries
countries_stats = pd.read_csv(DATA_PATH + "countries_stats.csv", encoding = "ISO-8859-1")


# # Getting the other tables:
# 
# - press_freedom_df : press freedom for each country from 2002  to 2018
# - corruption_df : corruption id  for each country from 2005 to 2017
# - gdp_df : gdp  for each country from 2005 to 2017
# - gini_df: gini for each country from 2005 to 2017
# - HDI  :Human Development Index  for each country from 2005 to 2017 
# 
# All the extraction and cleaning of the tables are done in function/getting_tables
# 
# 
# For press_freedom_df, we took the data from wikipedia, https://en.wikipedia.org/wiki/Press_Freedom_Index we copied the table to a text file: 'parse.txt' We created a small script to parse and convert these data to dataframe.

press_freedom_df, HDI , gini_df, gdp_df, corruption_df,protests_df_location = open_and_clean_data(DATA_PATH)


# During all these years , the indicators that were used to calculate all these indexes evolved. The metrics is different between 2005 and 2017. For example in 2013, Reporters Without  Borders changed their  index for press-freedom.As it is relative to other country, it is not changing the interpretation (lowest index = most free) 
 
# That mean that all these data have to be standardize before comparing between years.

# # Static visualizations:

# ### Visualizing average income per country on a world map

countries_topodata = json.load(open('data/countries.topojson.json'))

#getting the data from 2017
country_by_income_2017 = country_by_income_per_year[country_by_income_per_year['Year'] == 2017]


# As it's hard to visualualize through a dataframe, we will use a map:

#Displaying a map to visualize average income per country in the world
min_value = country_by_income_2017['Income Group'].min()
max_value = country_by_income_2017['Income Group'].max()
colormap = linear.YlGn_09.scale(min_value, max_value)
colormap.caption = 'Income per cap in 2017 (Low to high)'
location=[46.9,8.25]
x = 'Country Code'
y = 'Income Group'

results_map_income = folium_map(country_by_income_2017, x, y, location, countries_topodata, colormap, zoom=2)

results_map_income.save(FOLIUM_MAPS_PATH + 'results_map_income.html')
print("MAP 1/5: Static map about income in the US: created")

results_map_income


# Here, thanks to our visualization, we can estimate in which country the inhabitants have a better standard of living. Without any surprise, it's in the North America and in Europe

# ## Animated world map: visualyzing the kind of protest
# Displaying a dynamic world map which shows evolution day by day
# I also allows to see which kind of protest it is thanks to color indicators

#Extracting ActionGeo_Lat and ActionGeo_Long
protests_without_duplicated_values = protests_df_location
#protests_without_duplicated_values['ActionGeo_Lat'] = protests_df_location['ActionGeo_Lat']
#protests_without_duplicated_values['ActionGeo_Long'] = protests_df_location['ActionGeo_Long']

#Removing duplicated values 
#The values are not really duplicated, they took place on different day
#however we don't want to display a circle within another, we only want to visualyze the kind of protest
#we will visualize the frequency on the next two maps
protests_without_duplicated_values=protests_without_duplicated_values.drop_duplicates(subset=['ActionGeo_Long', 'ActionGeo_Lat', 'EventCode'], keep=False)
protests_without_duplicated_values=protests_without_duplicated_values.sort_values('SQLDATE')
protests_without_duplicated_values = filtering_df_date_country(protests_without_duplicated_values,date_start = 20140325,date_end = 20150800)

#getting only the first 3 digits of event code because we don't mind the other, they provide useless information for our analysis
protests_without_duplicated_values['EventCode']= protests_without_duplicated_values['EventCode'].astype(str)
protests_without_duplicated_values['EventCode']= protests_without_duplicated_values['EventCode'].str[0:3]


#getting a df in an appropriate format
protests_df_for_js = pd.DataFrame()
protests_df_for_js["coord_for_js"] = '[' + protests_without_duplicated_values['ActionGeo_Lat'].astype(str) + ',' + protests_without_duplicated_values['ActionGeo_Long'].astype(str) + '],'
protests_df_for_js["dates"] = protests_without_duplicated_values['SQLDATE'].astype(str)
protests_df_for_js["dates"] = '[' + protests_df_for_js['dates'].str[0:4] + protests_df_for_js['dates'].str[4:6] + protests_df_for_js['dates'].str[6:8] + '],'
protests_df_for_js["event_code"] = protests_without_duplicated_values['EventCode'].astype(str)
protests_df_for_js["event_code"] = '[' + protests_df_for_js['event_code'] + '],'

#Updating the js script to display result on a dynamic world map
updating_js_script(protests_df_for_js, WORLD_MAP_TYPE_PATH, markers_speed=0.1)


print("MAP 2/5: World Animated map that displays protests' kind day by day: created")


# The visualization above shows, day by day, each protest. We can see that, most of the time, the protest are a demonstrate or a rally. However, contrary to the rest of the world, in Europe, there a high percentage of protest related to politics. 
# 
# This kind of visualization allows to follow the protests' evolution and the type of each one (for rights, for a leadership change, is it a hunger strike, etc.)
# 
# Another information we could want is the frequency of each protest. To see it we choose a first implementation which shows the frequency through a color code:

# ## Animated world map: visualyzing the frequency
# Displaying a dynamic world map which shows how often we get a protest on an area.
# The color goes from white to green then black. Areas in white color means few protests took place here, black means the opposite.


protests_world_wanted = filtering_df_date_country(protests_df_location,date_start = 20150201,date_end = 20150220)
protests_world_wanted=protests_world_wanted.sort_values('SQLDATE')


#getting a dataframe with appropriate format
protests_world_wanted_for_js = getting_appropriate_format_df_for_js(protests_world_wanted)


#getting the number of time each value was repeted 
protests_world_wanted_for_js = adding_count_columns(protests_world_wanted_for_js)


protests_world_wanted_for_js['colors'] = ""
max_value = protests_world_wanted_for_js['count'].max()
min_value = protests_world_wanted_for_js['count'].min()
index = 0
for value in protests_world_wanted_for_js['coord_for_js']:
    number = protests_world_wanted_for_js['count'].iloc[index]
    protests_world_wanted_for_js.iloc[index, protests_world_wanted_for_js.columns.get_loc('colors')] = converting_count_to_color(min_value, max_value, number)
    index = index + 1

protests_world_wanted_for_js['colors'] = protests_world_wanted_for_js['colors'].astype(str)
protests_world_wanted_for_js["colors"] = '[' + protests_world_wanted_for_js['colors'] + '],'
for col in protests_world_wanted_for_js:
    protests_world_wanted_for_js[col] = protests_world_wanted_for_js[col].astype(str)

updating_js_script(protests_world_wanted_for_js, WORLD_MAP_FREQ_PATH, markers_number = 15, markers_speed=500)


print("MAP 3/5: World Animated map that displays protests's frequency day by day: created")


# Thanks to the visualization above, we can easily detect where the protests most appear. Let's take a relevant example: US presidential election period:


print("MAP 4/5: Animated map focused on the US that displays protests's frequency day by day: created")


# This visualization allow to know where the protests were the most frequent. We can guess that it correspond to the Clinton's electorate, we thus could locate the Clinton's electorate thanks to this visualization. We did this analysis on our blog: https://ada-project.school.blog/

# ## Animated map per country
# Displaying a map focused on a country.

# By showing the frequency with colors, we lost the information of the protests' kind. For the next kind of visualization, we kept the color code for the protests' type but we changed the way we are showing the frequency. We increased the circles' size each time a protest goes to a locate where other protests went.



country_wanted = "United States"

country_location = pd.read_csv(DATA_PATH + 'country_lat_long.csv')
for cln in country_location:
    country_location[cln] = country_location[cln].astype(str)
country_location['LatLong'] = '['+country_location['Latitude']+','+country_location['Longitude']+']'


s = pd.Series(country_location['Country Name'])
if country_wanted in s.unique():
    latlong = country_location[country_location['Country Name'].str.contains(country_wanted)]['LatLong']
    latlong = latlong.iloc[0]
else: 
    print("Country wanted doesn't exist")
protests_wanted = filtering_df_date_country(protests_df_location,date_start = 20160101,date_end = 20160201, country = country_wanted)

protests_wanted=protests_wanted.sort_values('SQLDATE')
protests_wanted['count'] = 0

#getting a dataframe with appropriate format
protests_wanted_for_js = getting_appropriate_format_df_for_js(protests_wanted)
#getting the number of time each value was repeted 
protests_wanted_for_js = adding_count_columns(protests_wanted_for_js)
protests_wanted_for_js['count'] = protests_wanted_for_js['count'].astype(str)
protests_wanted_for_js["count"] = '[' + protests_wanted_for_js['count'] + '],'

updating_js_script(protests_wanted_for_js, COUNTRY_MAP_PATH, markers_number=7, markers_speed=0.1, zoom="4", LatLong=latlong)

print("MAP 5/5: Animated map which displays protests' kind and frequency day by day in the US: created")


# Thanks to the visualization above we can visualize the frequency AND the protests' type.
# We adapt this map to a case study at the end of the notebook.
