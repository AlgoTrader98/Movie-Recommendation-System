
%pip install pandas



import pandas as pd

url = 'https://raw.githubusercontent.com/AlgoTrader98/Movie-Recommendation-System/main/Data/tmdb_5000_movies.csv'
movies = pd.read_csv(url)

import json
import ast

# convert the genre column to a list of dictionaries
movies['genres'] = movies['genres'].apply(lambda x: ast.literal_eval(x))

# extract the genre names into a new column
movies['genre_names'] = movies['genres'].apply(lambda x: [i['name'] for i in x])

# print the first 5 rows of the genre_names column
print(movies['genre_names'].head())

movies.head()
