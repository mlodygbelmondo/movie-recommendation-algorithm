import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

movies=pd.read_csv('dataset.csv')

movies.isnull().sum()

movies=movies[['id', 'title', 'overview', 'genre']]

movies['tags'] = movies['overview']+movies['genre']

mapped_movies = movies.drop(columns=['overview', 'genre'])

cv=CountVectorizer(max_features=10000, stop_words='english')

vector=cv.fit_transform(mapped_movies['tags'].values.astype('U')).toarray()

similarity=cosine_similarity(vector)

mapped_movies[mapped_movies['title']=="The Godfather"].index[0]

pickle.dump(movies, open('movies-data.pkl', 'wb'))
pickle.dump(similarity, open('similarity-model.pkl', 'wb'))