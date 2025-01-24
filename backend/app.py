from flask import Flask, request, jsonify, render_template
import pandas as pd
import re
import tiktoken
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import hstack, load_npz
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load and preprocess your dataset once when the application starts
df = pd.read_csv('data/movie_dataset.csv')
vectorizer = CountVectorizer()
title_matrix = vectorizer.fit_transform(df['title'].fillna(''))
genres_matrix = load_npz('data/genres_matrix.npz')
director_matrix = load_npz('data/director_matrix.npz')
cast_matrix = load_npz('data/cast_matrix.npz')
keywords_matrix = load_npz('data/keywords_matrix.npz')
tagline_matrix = load_npz('data/tagline_matrix.npz')
overview_matrix = load_npz('data/overview_matrix.npz')
combined_vector = hstack([genres_matrix, keywords_matrix, overview_matrix, tagline_matrix, cast_matrix, director_matrix])

scaler = StandardScaler(with_mean=False)
normalized_vector = scaler.fit_transform(combined_vector).toarray()

similarity_matrix = cosine_similarity(normalized_vector)
# similarity_matrix = load_npz('data/combined_vector.npz')

# Ensure genres_arr is properly set for all movies
df['genres_arr'] = df['genres'].apply(lambda x: x.split(' ') if isinstance(x, str) else [])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    movie_title = request.args.get('movie_title', '').lower()
    print(f"Retrieved Title: {movie_title}")

    def unrecognised_movie(movie_title):
        title_vector = vectorizer.transform([movie_title])
        similarity_scores = cosine_similarity(title_vector, title_matrix)
        similar_movies = list(enumerate(similarity_scores[0]))
        similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
        recommendation = [movie[0] for movie in similar_movies[1:6]]
        return recommendation

    def recommended(movie_title):
        row = df[df['title'] == movie_title]
        if row.empty:
            return unrecognised_movie(movie_title)
        movie_index = row.index[0]
        similar_movies = list(enumerate(similarity_matrix[movie_index]))
        similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
        return [movie[0] for movie in similar_movies[1:6]]

    recommendations = recommended(movie_title)
    if not recommendations:
        return jsonify({"error": "Movie not found"}), 404

    # Check if the columns exist before dropping them
    columns_to_drop = ['encoded_genres', 'encoded_keywords', 'encoded_cast', 'encoded_director']
    existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]

    recommended_movies = df.iloc[recommendations].drop(columns=existing_columns_to_drop)

    result = recommended_movies.replace({pd.NA: None, float('nan'): None}).to_dict(orient='records')
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)