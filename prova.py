import pandas as pd
import ast
import streamlit as st

movies = pd.read_csv('Data/moviedatafinal.csv')

def get_user_input():
    all_genres = set()
    for genres in movies['genre_names']:
        genre_list = ast.literal_eval(genres)
        for genre in genre_list:
            all_genres.add(genre.strip().lower())

    genres = st.multiselect("Select preferred genres", sorted(list(all_genres)))

    min_year = st.number_input("Minimum release year", value=1940)

    min_rating = st.slider("Minimum average rating", min_value=1.0, max_value=10.0, step=0.5, value=7.0)

    min_num_ratings = st.number_input("Minimum number of ratings", value=0, step=100)

    all_movie_titles = sorted(list(movies['title_x'].str.lower().unique()))
    movie1 = st.selectbox("Select the title of the first movie you like", all_movie_titles)
    movie2 = st.selectbox("Select the title of the second movie you like", all_movie_titles)

    return genres, min_year, min_rating, min_num_ratings, movie1, movie2


def filter_movies(genres, min_year, min_rating, min_num_ratings):
    filtered_movies = movies[movies['genre_names'].apply(lambda x: any(g.lower() in [y.lower() for y in ast.literal_eval(x)] for g in genres))]
    filtered_movies = filtered_movies[filtered_movies['release_year'] >= min_year]
    filtered_movies = filtered_movies[filtered_movies['vote_average'] >= min_rating]
    filtered_movies = filtered_movies[filtered_movies['vote_count'] >= min_num_ratings]
    return filtered_movies

def find_fitting_movies(filtered_movies, movie1, movie2):
    movie1_data = filtered_movies[filtered_movies['title_x'].str.lower() == movie1.lower()]
    movie2_data = filtered_movies[filtered_movies['title_x'].str.lower() == movie2.lower()]

    if movie1_data.empty or movie2_data.empty:
        return filtered_movies

    movie1_genres = set(ast.literal_eval(movie1_data.iloc[0]['genre_names']))
    movie2_genres = set(ast.literal_eval(movie2_data.iloc[0]['genre_names']))
    movie1_actors = set(ast.literal_eval(movie1_data.iloc[0]['actors']))
    movie2_actors = set(ast.literal_eval(movie2_data.iloc[0]['actors']))

    combined_genres = movie1_genres | movie2_genres
    combined_actors = movie1_actors | movie2_actors

    fitting_movies = filtered_movies[filtered_movies['genre_names'].apply(lambda x: any(g in [y for y in ast.literal_eval(x)] for g in combined_genres))]
    fitting_movies = fitting_movies[fitting_movies['actors'].apply(lambda x, actors=combined_actors: any(a in [y for y in ast.literal_eval(x)] for a in actors))]

    st.write("Fitting movies based on the selected genres and actors:")
    st.write(fitting_movies)

    return fitting_movies

def weighted_rating(movie, m, C):
    v = movie['vote_count']
    R = movie['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)

def recommend_movies(filtered_movies, num_recommendations=5):
    m = filtered_movies['vote_count'].quantile(0.75)
    C = filtered_movies['vote_average'].mean()

    filtered_movies['weighted_rating'] = filtered_movies.apply(weighted_rating, args=(m, C), axis=1)

    top_movies = filtered_movies.sort_values(by="weighted_rating", ascending=False).head(num_recommendations)

    st.write("Based on what you said, we recommend:")
    for idx, row in top_movies.iterrows():
        st.write(f"{row['title_x']} ({row['release_year']}) - Genres: {', '.join(ast.literal_eval(row['genre_names']))} - Weighted Rating: {row['weighted_rating']:.2f}")

def run_movie_recommendation_system():
    st.title("Movie Recommendation System")
    genres, min_year, min_rating, min_num_ratings, movie1, movie2 = get_user_input()
    if genres != []:
        filtered_movies = filter_movies(genres, min_year, min_rating, min_num_ratings)

        fitting_movies = find_fitting_movies(filtered_movies, movie1, movie2)

        recommend_movies(fitting_movies)

if __name__ == "__main__":
    run_movie_recommendation_system()
