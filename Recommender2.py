import pandas as pd
import pandas as pd
import ast
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

movies = pd.read_csv('Data/moviedatafinal.csv')


import pandas as pd
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import ast

def get_user_input(movies):
    all_genres = set()
    for genres in movies['genre_names']:
        genre_list = ast.literal_eval(genres)
        for genre in genre_list:
            all_genres.add(genre.strip().lower())

    genre_completer = WordCompleter(sorted(list(all_genres)), ignore_case=True)

    print("Please enter your preferred genres (separated by commas): ")
    genres = prompt("", completer=genre_completer).lower().split(', ')

    print("Please enter the minimum release year: ")
    min_year = int(input())

    print("Please enter the minimum average rating (1-10): ")
    min_rating = float(input())

    print("Please enter the minimum number of ratings: ")
    min_num_ratings = int(input())

    return genres, min_year, min_rating, min_num_ratings

def filter_movies(movies, genres, min_year, min_rating, min_num_ratings):
    filtered_movies = movies[movies['genre_names'].apply(lambda x: any(g.lower() in [y.lower() for y in ast.literal_eval(x)] for g in genres))]
    filtered_movies = filtered_movies[filtered_movies['release_year'] >= min_year]
    filtered_movies = filtered_movies[filtered_movies['vote_average'] >= min_rating]
    filtered_movies = filtered_movies[filtered_movies['vote_count'] >= min_num_ratings]
    return filtered_movies

def weighted_rating(movie, m, C):
    v = movie['vote_count']
    R = movie['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)

def recommend_movies(filtered_movies, num_recommendations=5):
    if filtered_movies.empty:
        print("No movies found based on your preferences.")
    else:
        m = filtered_movies['vote_count'].quantile(0.75)
        C = filtered_movies['vote_average'].mean()
        filtered_movies['weighted_rating'] = filtered_movies.apply(weighted_rating, args=(m, C), axis=1)
        top_movies = filtered_movies.sort_values(by="weighted_rating", ascending=False).head(num_recommendations)
        
        print("\nRecommended movies:")
        for idx, row in top_movies.iterrows():
            print(f"{row['title_x']} ({row['release_year']}) - Genres: {', '.join(ast.literal_eval(row['genre_names']))} - Weighted Rating: {row['weighted_rating']:.2f}")

def run_movie_recommendation_system():
    user_genres, min_year, min_rating, min_num_ratings = get_user_input(movies)
    filtered_movies = filter_movies(movies, user_genres, min_year, min_rating, min_num_ratings)
    recommend_movies(filtered_movies)

if __name__ == "__main__":
 
    run_movie_recommendation_system()

