import pandas as pd
import tiktoken
from flask import Flask, request, jsonify, render_template
import pandas as pd
import re
import tiktoken
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import hstack, save_npz, csr_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity



df = pd.read_csv('data/movie_dataset.csv')

print(df)


# Load and preprocess your dataset

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




dense_data = genres_matrix.toarray()  # Convert to numpy array
dense_data_as_list = dense_data.tolist()  # Convert to list
df['genre_matrix'] = dense_data_as_list



keywords_matrix = token_matrix_generator('keywords')[0]
dense_data = keywords_matrix.toarray()
dense_data_as_list = dense_data.tolist()
df['keywords_matrix'] = dense_data_as_list

overview_matrix = token_matrix_generator('overview')[0]
dense_data = overview_matrix.toarray()
dense_data_as_list = dense_data.tolist()
df['overview_matrix'] = dense_data_as_list

tagline_matrix = token_matrix_generator('tagline')[0]
dense_data = tagline_matrix.toarray()
dense_data_as_list = dense_data.tolist()
df['tagline_matrix'] = dense_data_as_list

title_matrix, _, _ = token_matrix_generator('title')
dense_data = title_matrix.toarray()
dense_data_as_list = dense_data.tolist()
df['title_matrix'] = dense_data_as_list

cast_matrix = token_matrix_generator('cast')[0]
dense_data = cast_matrix.toarray()
dense_data_as_list = dense_data.tolist()
df['cast_matrix'] = dense_data_as_list

director_matrix = token_matrix_generator('director')[0]
dense_data = director_matrix.toarray()
dense_data_as_list = dense_data.tolist()
df['director_matrix'] = dense_data_as_list

print(f'title matrix: {title_matrix}')
# print(genres_matrix)
combined_vector = hstack([genres_matrix, keywords_matrix, overview_matrix, tagline_matrix, cast_matrix, director_matrix])

scaler = StandardScaler(with_mean=False)
normalized_vector = scaler.fit_transform(combined_vector).toarray()

similarity_matrix = cosine_similarity(normalized_vector)

df['similarity_scores'] = similarity_matrix.tolist()


dense_data = genres_matrix.toarray()  # Convert to numpy array
dense_data_as_list = dense_data.tolist()  # Convert to list
df['genre_matrix'] = dense_data_as_list

# df.to_csv('data/processed_movie_dataset.csv', index=False)


print(df['cast_matrix'])
save_npz('data/title_matrix.npz', title_matrix)
save_npz('data/similarity_matrix.npz', csr_matrix(similarity_matrix))
print('saved')