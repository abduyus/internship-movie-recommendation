from flask import Flask, request, jsonify
import pandas as pd
import re
import tiktoken
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import hstack
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/recommend', methods=['GET'])
def recommend():
    # Get the movie title from the query parameters
    movie_title = request.args.get('movie_title', '').lower()

    # Step 1: Read the CSV file with appropriate parameters
    df = pd.read_csv('../../data/movie_dataset.csv')
    df['title'] = df['title'].str.lower()

    expected_columns = ['genres', 'keywords', 'cast', 'director']
    df = df[[col for col in df.columns if col in expected_columns or col not in expected_columns]]

    df['genres_arr'] = df['genres'].apply(lambda x: x.split(' ') if isinstance(x, str) else x)
    df['keywords_arr'] = df['keywords'].apply(lambda x: x.split(' ') if isinstance(x, str) else x)

    def split_into_pairs(text):
        if isinstance(text, str):
            return re.findall(r'\b\w+\s+\w+\b', text)
        return text

    df['cast_arr'] = df['cast'].apply(split_into_pairs)

    encoding = tiktoken.encoding_for_model('gpt-4o')

    df['encoded_genres'] = df['genres_arr'].apply(lambda x: [encoding.encode(item) for item in x] if isinstance(x, list) else [])
    df['encoded_keywords'] = df['keywords_arr'].apply(lambda x: [encoding.encode(item) for item in x] if isinstance(x, list) else [])
    df['encoded_cast'] = df['cast_arr'].apply(lambda x: [encoding.encode(item) for item in x] if isinstance(x, list) else [])
    df['encoded_director'] = df['director'].apply(lambda x: [encoding.encode(item) for item in x] if isinstance(x, list) else [])

    vectorizer = CountVectorizer()

    def token_matrix_generator(column):
        df[column] = df[column].fillna('')
        matrix_name = vectorizer.fit_transform(df[column])
        array_name = matrix_name.toarray()
        df_name = pd.DataFrame(array_name, columns=vectorizer.get_feature_names_out())
        return matrix_name, array_name, df_name

    df['tagline'] = df['tagline'].apply(lambda x: x if isinstance(x, str) else '')
    genres_matrix = token_matrix_generator('genres')[0]
    keywords_matrix = token_matrix_generator('keywords')[0]
    overview_matrix = token_matrix_generator('overview')[0]
    tagline_matrix = token_matrix_generator('tagline')[0]
    title_matrix = token_matrix_generator('title')[0]
    cast_matrix = token_matrix_generator('cast')[0]
    director_matrix = token_matrix_generator('director')[0]

    combined_vector = hstack([genres_matrix, keywords_matrix, overview_matrix, tagline_matrix, cast_matrix, director_matrix])

    scaler = StandardScaler(with_mean=False)
    normalized_vector = scaler.fit_transform(combined_vector).toarray()

    similarity_matrix = cosine_similarity(normalized_vector)

    def unrecognised_movie(movie_title):
        title_vector = vectorizer.transform([movie_title])
        similarity_scores = cosine_similarity(title_vector, title_matrix)
        similar_movies = list(enumerate(similarity_scores[0]))
        similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
        return [movie[0] for movie in similar_movies[1:6]]

    def recommended(movie_title):
        row = df[df['title'] == movie_title]
        if row.empty:
            return unrecognised_movie(movie_title)
        movie_index = row.index[0]
        similar_movies = list(enumerate(similarity_matrix[movie_index]))
        similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
        return [movie[0] for movie in similar_movies[1:6]]

    recommendations = recommended(movie_title)
    recommended_movies = df.iloc[recommendations]
    return jsonify(recommended_movies.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)