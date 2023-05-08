import pandas as pd
import ast
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv('Data/moviedatafinal.csv')

def get_user_input(movies):
    all_genres = set()
    for genres in movies['genre_names']:
        genre_list = ast.literal_eval(genres)
        for genre in genre_list:
            all_genres.add(genre.strip().lower())

    genre_completer = WordCompleter(sorted(list(all_genres)), ignore_case=True)

    print("Please enter your preferred genres (separated by commas): ")
    genres = prompt("", completer=genre_completer).lower().split(', ')

    print("Please enter the minimum release year < 2018: ")
    min_year = int(input())

    print("Please enter the minimum average rating (1-10): ")
    min_rating = float(input())

    print("Please enter the minimum number of ratings: ")
    min_num_ratings = int(input())

    # Autofill for movie titles
    all_movie_titles = sorted(list(movies['title_x'].str.lower().unique()))
    movie_title_completer = WordCompleter(all_movie_titles, ignore_case=True)
    
    print("Please enter the title of the first movie you like: ")
    movie1 = prompt("", completer=movie_title_completer)

    print("Please enter the title of the second movie you like: ")
    movie2 = prompt("", completer=movie_title_completer)

    return genres, min_year, min_rating, min_num_ratings, movie1, movie2


def filter_movies(movies, genres, min_year, min_rating, min_num_ratings, movie1, movie2):
    filtered_movies = movies[movies['genre_names'].apply(lambda x: any(g.lower() in [y.lower() for y in ast.literal_eval(x)] for g in genres))]
    filtered_movies = filtered_movies[filtered_movies['release_year'] >= min_year]
    filtered_movies = filtered_movies[filtered_movies['vote_average'] >= min_rating]
    filtered_movies = filtered_movies[filtered_movies['vote_count'] >= min_num_ratings]
    filtered_movies = filtered_movies[(filtered_movies['title_x'].str.lower() == movie1.lower()) & (filtered_movies['title_x'].str.lower() == movie2.lower())]


    return filtered_movies



def find_fitting_movies(filtered_movies, movie1, movie2):
    # Get the data for the input movies
    movie1_data = filtered_movies[filtered_movies['title_x'].str.lower() == movie1.lower()]
    movie2_data = filtered_movies[filtered_movies['title_x'].str.lower() == movie2.lower()]

    if movie1_data.empty or movie2_data.empty:
        return filtered_movies

    # Combine the genres and actors from both input movies
    movie1_genres = set(ast.literal_eval(movie1_data.iloc[0]['genre_names']))
    movie2_genres = set(ast.literal_eval(movie2_data.iloc[0]['genre_names']))
    movie1_actors = set(ast.literal_eval(movie1_data.iloc[0]['actors']))
    movie2_actors = set(ast.literal_eval(movie2_data.iloc[0]['actors']))

    combined_genres = movie1_genres | movie2_genres
    combined_actors = movie1_actors | movie2_actors

    # Compute the cosine similarity between each movie and the input movies
    movie_titles = filtered_movies['title_x'].tolist()
    movie_features = filtered_movies['genre_names'] + filtered_movies['actors']
    input_movie_features = [', '.join(combined_genres) + ', ' + ', '.join(combined_actors)] * len(movie_titles)

    vectorizer = CountVectorizer().fit_transform(movie_features + input_movie_features)
    similarity_matrix = cosine_similarity(vectorizer)

    # Calculate the scores for each movie based on its similarity to the input movies
    movie_scores = []
    for i, title in enumerate(movie_titles):
        if title.lower() in [movie1.lower(), movie2.lower()]:
            # Don't recommend the input movies themselves
            continue
        score = similarity_matrix[-1, i]
        movie_scores.append((title, score))

    # Sort the movies by score and return the top ones
    movie_scores.sort(key=lambda x: x[1], reverse=True)
    top_movie_titles = [x[0] for x in movie_scores[:5]]
    fitting_movies = filtered_movies[filtered_movies['title_x'].isin(top_movie_titles)]

    return fitting_movies


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
    user_genres, min_year, min_rating, min_num_ratings, movie1, movie2 = get_user_input(movies)
    filtered_movies = filter_movies(movies, user_genres, min_year, min_rating, min_num_ratings, movie1, movie2)
    fitting_movies = find_fitting_movies(filtered_movies, movie1, movie2)
    recommend_movies(fitting_movies)


if __name__ == "__main__":
    run_movie_recommendation_system()