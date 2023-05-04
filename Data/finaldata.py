
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

# %%
url = "https://raw.githubusercontent.com/AlgoTrader98/Movie-Recommendation-System/main/Data/tmdb_5000_credits.csv"
credits = pd.read_csv(url)



# %%
movies.release_date


# %%
str(movies.release_date)

# %%
# drop rows with missing values
movies.dropna(subset=['release_date'], inplace=True)

# convert release_date to datetime format and extract year
movies['release_year'] = pd.to_datetime(movies['release_date'], errors='coerce').dt.year.astype('Int64')


# %%
movies

# %%
credits

# %%
import ast

cast_names = []

for cast in credits['cast']:
    cast_dict = ast.literal_eval(cast)
    names = [actor['name'].strip() for actor in cast_dict if 'name' in actor]
    cast_names.append(names)

print(cast_names)


# %%
import ast

credits['cast_names'] = ''

for i, cast in enumerate(credits['cast']):
    cast_dict = ast.literal_eval(cast)
    names = [actor['name'].strip() for actor in cast_dict if 'name' in actor]
    credits['cast_names'][i] = names


# %%
credits

# %%
movies

# %%
import ast
import pandas as pd

# Extract cast_names from credits data frame
cast_names = []
for cast in credits['cast']:
    cast_dict = ast.literal_eval(cast)
    names = [actor['name'].strip() for actor in cast_dict if 'name' in actor]
    cast_names.append(names)

# Add cast_names as a new column in credits data frame
credits['cast_names'] = cast_names

# Merge credits and movies data frames on movie_id and id columns, respectively
merged_df = credits.merge(movies, left_on='movie_id', right_on='id', how='left')

# Apply a lambda function to cast_names column to fill in missing values with an empty list
merged_df['cast_names'] = merged_df['cast_names'].apply(lambda x: x if isinstance(x, list) else [])


# %%
merged_df.rename(columns={'cast_names': 'actors'}, inplace=True)
movies = merged_df
movies



