from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pickle

movies_data = pickle.load(open("movies-data.pkl", 'rb'))
similarity_model = pickle.load(open("similarity-model.pkl", 'rb'))

app = Flask(__name__)
cors = CORS(app)

@cross_origin()
@app.route('/getRecommendedMovies/<int:movieId>', methods=['GET'])
def predict(movieId):
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

    try:
        result = get_recommended_movies(movieId, 30)

        return jsonify({"movieId": movieId, "recommendations": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)
