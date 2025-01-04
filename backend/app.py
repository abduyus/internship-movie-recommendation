from flask import Flask, request, jsonify, render_template
import pandas as pd
import re
import tiktoken
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import hstack
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    movie_title = request.args.get('movie_title', '').lower()
    print(f"Retrieved Title: {movie_title}")

    # Load and preprocess your dataset
    df = pd.read_csv('data/movie_dataset.csv')
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
    title_matrix, _, _ = token_matrix_generator('title')
    cast_matrix = token_matrix_generator('cast')[0]
    director_matrix = token_matrix_generator('director')[0]

    print(f'title matrix: {title_matrix}')
    # print(genres_matrix)
    combined_vector = hstack([genres_matrix, keywords_matrix, overview_matrix, tagline_matrix, cast_matrix, director_matrix])

    scaler = StandardScaler(with_mean=False)
    normalized_vector = scaler.fit_transform(combined_vector).toarray()

    similarity_matrix = cosine_similarity(normalized_vector)

    def unrecognised_movie(movie_title):
        title_matrix = vectorizer.fit_transform(df['title'].fillna(''))

        # Step 2: Transform the input title
        title_vector = vectorizer.transform([movie_title])

        # Step 3: Compute cosine similarity
        similarity_scores = cosine_similarity(title_vector, title_matrix)

        # Output similarity scores
        print(similarity_scores)
        similar_movies = list(enumerate(similarity_scores[0]))
        print(similar_movies)
        similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
        print(similar_movies)
        recommendation = [movie[0] for movie in similar_movies[1:6]]
        print(recommendation)
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

    recommended_movies = df.iloc[recommendations].drop(
        columns=['crew', 'encoded_genres', 'encoded_keywords', 'encoded_cast', 'encoded_director']
    )

    # Replace NaN with None for valid JSON
    result = recommended_movies.replace({pd.NA: None, float('nan'): None}).to_dict(orient='records')
    # print(result)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)