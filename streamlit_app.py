import streamlit as st
import pandas as pd
import ast
from prompt_toolkit.completion import WordCompleter

import pandas as pd
import ast
import streamlit as st
movies = pd.read_csv('Data/moviedatafinal.csv')

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles.css")


def get_user_input(movies):
    all_genres = set()
    for genres in movies['genre_names']:
        genre_list = ast.literal_eval(genres)
        for genre in genre_list:
            all_genres.add(genre.strip().lower())

    genres = st.multiselect("Please select your preferred genres", options=sorted(list(all_genres)), key="genres_multiselect")
    min_year = st.slider("Please enter the minimum release year", min_value=1900, max_value=2017, value=2000)
    min_rating = st.slider("Please enter the minimum average rating", min_value=1.0, max_value=10.0, value=5.0)
    min_num_ratings = st.slider("Please enter the minimum number of ratings", min_value=0, max_value=1000, value=10)
    
    movie_titles = sorted(movies['title_x'].unique())
    movie_titles = sorted(movies['title_x'].unique())
    movie1 = st.selectbox("Select the first movie you like", options=movie_titles, key="movie1_selectbox")
    movie2 = st.selectbox("Select the second movie you like", options=movie_titles, key="movie2_selectbox")

    return genres, min_year, min_rating, min_num_ratings, movie1, movie2



def filter_movies(movies, genres, min_year, min_rating, min_num_ratings):
    filtered_movies = movies[movies['genre_names'].apply(lambda x: any(g.lower() in [y.lower() for y in ast.literal_eval(x)] for g in genres))]
    filtered_movies = filtered_movies[filtered_movies['release_year'] >= min_year]
    filtered_movies = filtered_movies[filtered_movies['vote_average'] >= min_rating]
    filtered_movies = filtered_movies[filtered_movies['vote_count'] >= min_num_ratings]
    return filtered_movies


def filter_movies_by_user_movies(movies, movie1, movie2):
    movie1_data = movies[movies['title_x'].str.lower() == movie1.lower()]
    movie2_data = movies[movies['title_x'].str.lower() == movie2.lower()]

    if movie1_data.empty or movie2_data.empty:
        return pd.DataFrame()

    movie1_genres = set(ast.literal_eval(movie1_data.iloc[0]['genre_names']))
    movie2_genres = set(ast.literal_eval(movie2_data.iloc[0]['genre_names']))
    movie1_actors = set(ast.literal_eval(movie1_data.iloc[0]['actors']))
    movie2_actors = set(ast.literal_eval(movie2_data.iloc[0]['actors']))

    combined_genres = movie1_genres | movie2_genres
    combined_actors = movie1_actors | movie2_actors

    filtered_movies = movies[movies['genre_names'].apply(lambda x: any(g in [y for y in ast.literal_eval(x)] for g in combined_genres))]
    filtered_movies = filtered_movies[filtered_movies['actors'].apply(lambda x: any(a in [y for y in ast.literal_eval(x)] for a in combined_actors))]

    return filtered_movies

def weighted_rating(movie, m, C):
    v = movie['vote_count']
    R = movie['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)

def recommend_movies(filtered_movies, num_recommendations=5):
    if filtered_movies.empty:
        print("No movies found based on your preferences.")
        return pd.DataFrame()  # Return an empty DataFrame
    else:
        m = filtered_movies['vote_count'].quantile(0.75)
        C = filtered_movies['vote_average'].mean()
        filtered_movies['weighted_rating'] = filtered_movies.apply(weighted_rating, args=(m, C), axis=1)
        top_movies = filtered_movies.sort_values(by="weighted_rating", ascending=False).head(num_recommendations)

        return top_movies  # Return the recommended movies DataFrame

def run_movie_recommendation_system():
        user_genres, min_year, min_rating, min_num_ratings, movie1, movie2 = get_user_input(movies)
        filtered_movies = filter_movies(movies, user_genres, min_year, min_rating, min_num_ratings)
        fitting_movies = find_fitting_movies(filtered_movies, movie1, movie2)
        recommend_movies(fitting_movies)


def main():
    
    with st.expander("Meet the Developers"):
        st.write("""
        Our team of talented developers consists of four members, each bringing their unique skills and expertise to create this movie recommendation system.
        """)

        st.write("""
        - **Jan-Niclas**: A data scientist and machine learning expert, Jan-Niclas is responsible for designing the recommendation algorithms and filtering techniques.
        - **Luis**: A full-stack developer, Luis focuses on the back-end functionality of the app and ensures a smooth user experience.
        - **Tommaso**: A front-end developer and UX designer, Tommaso is in charge of creating the user interface and ensuring the app looks and feels professional.
        - **Lulu**: A database specialist, Lulu is responsible for maintaining and updating the movie dataset used by the app.
        """)        
            
    st.title("Movie Recommendation System")

    st.write("""
    Welcome to the Movie Recommendation System! This app helps you find movies you might enjoy based on your preferences and favorite movies. To get started, simply enter your preferences below and select two movies you like. The app will then recommend five movies that match your preferences and taste.
    """)

    st.subheader("Enter your preferences:")

    st.write("""
    * **Genres**: Choose one or more genres you prefer. The app will recommend movies from these genres.
    * **Minimum Release Year**: Select the earliest release year you are interested in. The app will recommend movies released in or after the selected year.
    * **Minimum Average Rating**: Choose the lowest average rating you will accept. The app will recommend movies with a rating equal to or higher than your selection.
    * **Minimum Number of Ratings**: Select the minimum number of ratings a movie must have to be considered. The app will recommend movies with at least this many ratings.
    * **First and Second Movie**: Choose two movies you like. The app will use these selections to find movies that share similar genres and actors.
    """)

    genres, min_year, min_rating, min_num_ratings, movie1, movie2 = get_user_input(movies)

    st.subheader("Filtering movies based on your movie preferences...")
    filtered_movies_by_user_movies = filter_movies_by_user_movies(movies, movie1, movie2)

    if filtered_movies_by_user_movies.empty:
        st.write("No movies found based on your movie preferences.")
    else:
        st.subheader("Filtering movies based on your other preferences...")
        filtered_movies = filter_movies(filtered_movies_by_user_movies, genres, min_year, min_rating, min_num_ratings)

        st.subheader("Recommended movies:")
        recommended_movies = recommend_movies(filtered_movies)

        if recommended_movies.empty:
            st.write("No movies found based on your preferences.")
        else:
            for idx, row in recommended_movies.iterrows():
                movie_card = f"""
                <div class="movie-card">
                    <h4>{row['title_x']} ({row['release_year']})</h4>
                    <p>Genres: {', '.join(ast.literal_eval(row['genre_names']))}</p>
                    <p>Weighted Rating: {row['weighted_rating']:.2f}</p>
                </div>
                """
                st.markdown(movie_card, unsafe_allow_html=True)
             

if __name__ == "__main__":
    main()
