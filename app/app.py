from flask import Flask, request, jsonify
from flask_cors import CORS
from models.models import Movie, User, UserFriend, Review
from extensions import db
from utils import map_movie, get_recommended_movies

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@localhost/MovieDb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# add cors
CORS(app)

@app.route('/getMainPageData/<userId>', methods=['GET'])
def get_main_page_data(userId):
    try:
        movieId = 550
        movie = Movie.query.where(Movie.Tmdb_Id == movieId).first()

        result = get_recommended_movies(movieId, 30)

        recommended_movie = Movie.query.where(Movie.Tmdb_Id.in_(result)).all()
        
        mapped_recommended_movie = [map_movie(r) for r in recommended_movie]
        mapped_movies = map_movie(movie)

        recommendations_section = {
            "movie": mapped_movies,
            "recommendations": mapped_recommended_movie
        }

        popular_movie = Movie.query.order_by(Movie.Popularity.desc()).limit(30).all()
        mapped_popular_movies = [map_movie(m) for m in popular_movie]

        inception = Movie.query.where(Movie.Tmdb_Id == 27205).first()
        shawshank = Movie.query.where(Movie.Tmdb_Id == 278).first()
        godfather = Movie.query.where(Movie.Tmdb_Id == 238).first()

        friend1_name = "Jakub Wajstak"
        friend2_name = "Paweł Dyśko"
        friend3_name = "Wiktor Rzeźnicki"

        friends_activity = [
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
        ]

        return jsonify({"recommendations_section": recommendations_section, "popular_movies_section": mapped_popular_movies, "friends_activity_section": friends_activity})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/getRecommendedMovie/<movieId>', methods=['GET'])
def get_movie(movieId):
    try:
        print(movieId)
        movie = Movie.query.where(Movie.Id == movieId).first()

        result = get_recommended_movies(movie.Tmdb_Id, 30)
        recommended_movie = Movie.query.where(Movie.Tmdb_Id.in_(result)).all()

        mapped_recommended_movie = [map_movie(r) for r in recommended_movie]

        return jsonify({"movieId": movieId, "recommendations": mapped_recommended_movie})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
@app.route('/getSocialPageData/<userId>', methods=['GET'])
def get_social_page_data(userId):
    try:
        # user = Users.query.where(Users.Id == userId).first()
        # friends = user.friends

        # friend_ids = [f.Id for f in friends]
        # friend_movie = Movie.query.where(Movie.UserId.in_(friend_ids)).all()

        # mapped_friend_movie = [map_movie(f) for f in friend_movie]

        inception = Movie.query.where(Movie.Tmdb_Id == 27205).first()
        shawshank = Movie.query.where(Movie.Tmdb_Id == 278).first()
        godfather = Movie.query.where(Movie.Tmdb_Id == 238).first()

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
    
@app.route('/getAllMovies/', methods=['GET'])
@app.route('/getAllMovies/<search>', methods=['GET'])
def get_all_movie(search=None):
    try:
        if search is None:
            movie = Movie.query.all()
        else:
            movie = Movie.query.where(Movie.Title.ilike(f"%{search}%")).all()
        mapped_movies = [map_movie(m) for m in movie[0:10]]

        return jsonify(mapped_movies)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return jsonify([{'id': user.Id, 'name': user.Login} for user in users])

@app.route('/getFriends/<userId>', methods=['GET'])
def get_friends(userId: str):
    # Query for friends where the user is the requester
    friends_as_user = db.session.query(User).join(UserFriend, User.Id == UserFriend.FriendId).filter(
        UserFriend.UserId == userId, UserFriend.Status == 1
    )
    # Query for friends where the user is the recipient
    friends_as_friend = db.session.query(User).join(UserFriend, User.Id == UserFriend.UserId).filter(
        UserFriend.FriendId == userId, UserFriend.Status == 1
    )
     # Combine the two queries using `union`
    all_friends = friends_as_user.union(friends_as_friend)

     # Map names
    return [{"id": f.Id, "name": f.Login} for f in all_friends.all()]
    
# get all users that are not your friends
@app.route('/getNonFriends/<userId>', methods=['GET'])
def get_non_friends(userId: str):
    # Query for friends where the user is the requester
    friends_as_user = db.session.query(User).join(UserFriend, User.Id == UserFriend.FriendId).filter(
        UserFriend.UserId == userId, UserFriend.Status == 1
    )
    # Query for friends where the user is the recipient
    friends_as_friend = db.session.query(User).join(UserFriend, User.Id == UserFriend.UserId).filter(
        UserFriend.FriendId == userId, UserFriend.Status == 1
    )
    # Combine the two queries using `union`
    all_friends = friends_as_user.union(friends_as_friend)

    all_users = User.query.all()
    non_friends = [user for user in all_users if user not in all_friends.all()]

    # for every non friend get their mutual friends count and append it to the non friends list
    non_friends_with_mutual_friends = []
    for non_friend in non_friends:
        mutual_friends_as_user = db.session.query(User).join(UserFriend, User.Id == UserFriend.FriendId).filter(
            UserFriend.UserId == non_friend.Id, UserFriend.Status == 1
        ).count()
        mutual_friends_as_friend = db.session.query(User).join(UserFriend, User.Id == UserFriend.UserId).filter(
            UserFriend.FriendId == non_friend.Id, UserFriend.Status == 1
        ).count()
        non_friends_with_mutual_friends.append({"id": non_friend.Id, "name": non_friend.Login, "mutualFriends": mutual_friends_as_user + mutual_friends_as_friend})
    
    return non_friends_with_mutual_friends

# get pending friend requests
@app.route('/getPendingFriendRequests/<userId>', methods=['GET'])
def get_pending_friend_requests(userId: str):
    # Query for friends where the user is the recipient
    pending_requests = db.session.query(User).join(UserFriend, User.Id == UserFriend.UserId).filter(
        UserFriend.FriendId == userId, UserFriend.Status == 0
    )

    # for every friend request get their mutual friends count and append it to the pending requests list
    pending_requests_with_mutual_friends = []
    for pending_request in pending_requests.all():
        mutual_friends_as_user = db.session.query(User).join(UserFriend, User.Id == UserFriend.FriendId).filter(
            UserFriend.UserId == pending_request.Id, UserFriend.Status == 1
        ).count()
        mutual_friends_as_friend = db.session.query(User).join(UserFriend, User.Id == UserFriend.UserId).filter(
            UserFriend.FriendId == pending_request.Id, UserFriend.Status == 1
        ).count()
        pending_requests_with_mutual_friends.append({"id": pending_request.Id, "name": pending_request.Login, "mutualFriends": mutual_friends_as_user + mutual_friends_as_friend})
    
    return pending_requests_with_mutual_friends

# remove friend and check both sides of the relationship
@app.route('/removeFriend/<userId>/<friendId>', methods=['DELETE'])
def remove_friend(userId: str, friendId: str):
    friend = UserFriend.query.filter_by(UserId=userId, FriendId=friendId).first()
    if friend is None:
        friend = UserFriend.query.filter_by(UserId=friendId, FriendId=userId).first()
    db.session.delete(friend)
    db.session.commit()
    return {"message": "Friend removed"}    
    

# Get reviews for a movie, return reviewer name, review comment, review rating, and sort by the newest date
@app.route('/getReviews/<movieId>', methods=['GET'])
def get_reviews(movieId: str):
    reviews = Review.query.where(Review.MovieId == movieId).order_by(Review.Date.desc()).all()
    return [{"reviewer": review.User.Login, "comment": review.Comment, "rating": review.Rating, "id": review.Id} for review in reviews]



if __name__ == '__main__':
    app.run(port=5001, debug=True)
