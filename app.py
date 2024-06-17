import pickle
import streamlit as st
import requests
import re
import pandas as pd

def fetch_poster(movie_name):
    pattern=r'[\w\s:-]+'
    movie_name = re.search(pattern,movie_name).group().strip()
    print(movie_name)
    url = 'https://api.themoviedb.org/3/search/movie'
    params = {
        'query': movie_name,
        'api_key': '8265bd1679663a7ea12ac168da84d2e8', 
        'language': 'en-US'
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(data)
    movie = data['results'][0]
    poster_path = movie.get('poster_path')
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def get_recommendations(user_id, cosine_sim, user_movie_matrix, merge_df, top_N=5):
    user_similarity = cosine_sim[user_id]
    user_similarity_df = pd.DataFrame({'userId': user_movie_matrix.index, 'similarity': user_similarity.values})
    user_similarity_df = user_similarity_df[user_similarity_df['userId'] != user_id]
    user_similarity_df = user_similarity_df.sort_values(by='similarity', ascending=False)
    similar_user_ratings = pd.merge(user_similarity_df, user_movie_matrix, left_on='userId', right_index=True)
    similar_user_ratings.set_index('userId', inplace=True)
    weighted_ratings = similar_user_ratings.mul(similar_user_ratings['similarity'], axis=0)
    sum_of_similarity = similar_user_ratings['similarity'].sum()
    recommended_movies = weighted_ratings.sum() / sum_of_similarity
    recommended_movies = recommended_movies.sort_values(ascending=False)
    user_rated_movies = merge_df[merge_df['userId'] == user_id]['title']
    recommended_movies = recommended_movies[~recommended_movies.index.isin(user_rated_movies)]
    # Get the top 5 similar movies
    recommended_movie_names = [movie for movie in recommended_movies.head(top_N).index]
    recommended_movie_posters = []
    for movie in recommended_movie_names:
        # fetch the movie poster
        #print(fetch_poster(movie))
        recommended_movie_posters.append(fetch_poster(movie))
    return recommended_movie_names, recommended_movie_posters

cosine_sim = pickle.load(open('cosine_sim.pkl', 'rb'))
user_movie_matrix = pickle.load(open('user_movie_matrix.pkl', 'rb'))
merge_df = pickle.load(open('merge_df.pkl', 'rb'))

st.set_page_config(
    page_title="Movie Recommender System",
    layout="centered",
)

st.header('Movie Recommender System')
input_text = st.text_input("Enter UserID:", key="int", max_chars=3)

if st.button("Show Recommendations"):
    if len(input_text)==0:
        st.error("No UserID Entered!!!")
    else:
        try:
            if (int(input_text) in range(611)) :
                #st.markdown("Good")
                recommended_movie_names, recommended_movie_posters = get_recommendations(int(input_text), cosine_sim, user_movie_matrix, merge_df)
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.text(recommended_movie_names[0])
                    st.image(recommended_movie_posters[0])
                with col2:
                    st.text(recommended_movie_names[1])
                    st.image(recommended_movie_posters[1])
                with col3:
                    st.text(recommended_movie_names[2])
                    st.image(recommended_movie_posters[2])
                with col4:
                    st.text(recommended_movie_names[3])
                    st.image(recommended_movie_posters[3])
                with col5:
                    st.text(recommended_movie_names[4])
                    st.image(recommended_movie_posters[4])
            else:
                st.error("UserID out of range!!!")
        except ValueError:
            # when you enter something shit
            st.error("Invalid UserID!!!")

