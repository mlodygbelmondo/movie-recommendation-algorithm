import pickle
movies_data = pickle.load(open("movies-data.pkl", 'rb'))
similarity_model = pickle.load(open("similarity-model.pkl", 'rb'))

def get_recommended_movies(movie_id, amount_of_movies):
    index=movies_data[movies_data['id']==movie_id].index[0]
    distance = sorted(list(enumerate(similarity_model[index])), reverse=True, key=lambda vector:vector[1])
    recommended_movies = []
    for i in distance[0:amount_of_movies+1]:
        recommended_movies.append(movies_data.iloc[i[0]].id)
    recommended_movies.remove(movie_id)
    return recommended_movies

# print(get_recommended_movies(335984, 10))