import pickle
movies_data = pickle.load(open("movies-data.pkl", 'rb'))
similarity_model = pickle.load(open("similarity-model.pkl", 'rb'))

def map_movie(movie):
    return {
        'id': movie.Id,
        'title': movie.Title,
        'description': movie.Description,
        'release_date': movie.ReleaseDate,
        'duration': movie.Duration,
        'image': movie.Image,
        'box_office': movie.BoxOffice,
        'popularity': movie.Popularity,
        'tmdb_id': movie.Tmdb_Id,
        'genre': movie.Genre
    }

def get_recommended_movies(movie_id, amount_of_movies):
    if movie_id not in movies_data['id'].values:
        raise ValueError(f"Movie ID {movie_id} not found in dataset")
    
    index = movies_data[movies_data['id'] == movie_id].index[0]

    distances = sorted(
        list(enumerate(similarity_model[index])),
        reverse=True,
        key=lambda vector: vector[1]
    )

    recommended_movies = [
        int(movies_data.iloc[i[0]].id) for i in distances[:amount_of_movies + 1]
    ]

    if movie_id in recommended_movies:
        recommended_movies.remove(movie_id)
    return recommended_movies[:amount_of_movies]