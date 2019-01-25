# About:
In this project, wrangling and cleaning of a OpenStreetMap [dataset](https://download.bbbike.org/osm/bbbike/Cairo/Cairo.osm.mapsforge-osm.zip/) are performed. The data is then imported to a SQLite database for querying.

# Data overview:
In accordance with the OSM XML API, the data consists of three main types of elements:

* Nodes
* Ways
* Relations

**Problems encountered in the dataset:**
* "arabic": tags with Arabic characters
* "lower": tags that contain only lowercase letters and are valid
* "lower_colon": otherwise valid tags with a colon in their names
* "odd_chars": tags with odd characters
* "other": other tags that do not fall into the other three categories

# Files:
*overview.py*: This script gets an initial idea of the number and names of tags in the dataset.

*audit.py*: This script contains the required auditing before the data cleaning.

*clean.py*: This script performs the real cleaning operations on the data.

*exploration.ipynb* : This script explores some basic stats and city insights.
