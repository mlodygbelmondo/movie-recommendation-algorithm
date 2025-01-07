from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from models.movies import Movies
from models.users import Users
from extensions import db
from utils import map_movie, get_recommended_movies

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@localhost/MovieDb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

CORS(app)

@app.route('/getMainPageData/<userId>', methods=['GET'])
def predict(userId):
    try:
        movieId = 550
        movie = Movies.query.where(Movies.Tmdb_Id == movieId).first()

        result = get_recommended_movies(movieId, 30)

        recommended_movies = Movies.query.where(Movies.Tmdb_Id.in_(result)).all()
        
        mapped_recommended_movies = [map_movie(r) for r in recommended_movies]
        mapped_movie = map_movie(movie)

        recommandations_section = {
            "movie": mapped_movie,
            "recommendations": mapped_recommended_movies
        }

        popular_movies = Movies.query.order_by(Movies.Popularity.desc()).limit(30).all()
        mapped_popular_movies = [map_movie(m) for m in popular_movies]

        return jsonify({"recommendations_section": recommandations_section, "popular_movies": mapped_popular_movies})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/getRecommendedMovies/<movieId>', methods=['GET'])
def get_movies(movieId):
    try:
        print(movieId)
        movie = Movies.query.where(Movies.Id == movieId).first()

        result = get_recommended_movies(movie.Tmdb_Id, 30)
        recommended_movies = Movies.query.where(Movies.Tmdb_Id.in_(result)).all()

        mapped_recommended_movies = [map_movie(r) for r in recommended_movies]

        return jsonify({"movieId": movieId, "recommendations": mapped_recommended_movies})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
@app.route('/getSocialPageData/<userId>', methods=['GET'])
def get_social_page_data(userId):
    try:
        # user = Users.query.where(Users.Id == userId).first()
        # friends = user.friends

        # friend_ids = [f.Id for f in friends]
        # friend_movies = Movies.query.where(Movies.UserId.in_(friend_ids)).all()

        # mapped_friend_movies = [map_movie(f) for f in friend_movies]

        inception = Movies.query.where(Movies.Tmdb_Id == 27205).first()
        shawshank = Movies.query.where(Movies.Tmdb_Id == 278).first()
        godfather = Movies.query.where(Movies.Tmdb_Id == 238).first()

        friend1_name = "Jakub Wajstak"
        friend2_name = "Paweł Dyśko"
        friend3_name = "Wiktor Rzeźnicki"

        return jsonify([
            {
                "friend_name": friend1_name,
                "movie": map_movie(inception),
                "action": "Dodał do Ulubionych",
            },
            {
                "friend_name": friend2_name,
                "movie": map_movie(shawshank),
                "action": "Dodał do Do Obejrzenia",
            },
            {
                "friend_name": friend3_name,
                "movie": map_movie(godfather),
                "action": "Obejrzał",
            }
        ])
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500    
    
@app.route('/', methods=['GET'])
def index():
    users = Users.query.all()
    return jsonify([{'id': user.Id, 'name': user.Login} for user in users])

# def get_friends(user_id: str):
#     # Query for friends where the user is the requester
#     friends_as_user = db.session.query(Users).join(UserFriends, Users.Id == UserFriends.FriendId).filter(
#         UserFriends.UserId == user_id, UserFriends.Status == Status.Accepted
#     )

#     # Query for friends where the user is the recipient
#     friends_as_friend = db.session.query(Users).join(UserFriends, Users.Id == UserFriends.UserId).filter(
#         UserFriends.FriendId == user_id, UserFriends.Status == Status.Accepted
#     )

#     # Combine the two queries using `union`
#     all_friends = friends_as_user.union(friends_as_friend)

#     return all_friends.all()


if __name__ == '__main__':
    app.run(port=5001, debug=True)
