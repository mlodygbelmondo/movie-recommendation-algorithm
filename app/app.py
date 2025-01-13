from flask import Flask, request, jsonify
from flask_cors import CORS
from models.models import Movie, User, UserFriend, Review, FavoriteMovie
from sqlalchemy import not_
from extensions import db
from utils import map_movie, get_recommended_movies, get_newest_liked_movie, get_user_social_data

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
        # get last favorite movie ordered by CreatedAt, return movie
        last_favorite_movie = FavoriteMovie.query.where(FavoriteMovie.UserId == userId).order_by(FavoriteMovie.CreatedAt.desc()).first()
        # get last highly rated movie where rating is over or equal 4 ordered by CreatedAt, return movie
        last_highly_rated_movie = Review.query.where(Review.UserId == userId, Review.Rating >= 4).order_by(Review.CreatedAt.desc()).first()

        movie = get_newest_liked_movie(last_favorite_movie, last_highly_rated_movie)

        recommendations_section = None

        if movie is not None:       
            result = get_recommended_movies(movie.Tmdb_Id, 30)

            recommended_movies = Movie.query.where(Movie.Tmdb_Id.in_(result)).all()
        
            mapped_recommended_movie = [map_movie(r) for r in recommended_movies]
            mapped_movie = map_movie(movie)

            recommendations_section = {
                "movie": mapped_movie,
                "recommendations": mapped_recommended_movie
            }

        popular_movies = Movie.query.order_by(Movie.Popularity.desc()).limit(30).all()
        mapped_popular_movies = [map_movie(m) for m in popular_movies]

        friends_activity = get_user_social_data(userId)[:30]

        return jsonify({"recommendations_section": recommendations_section, "popular_movies_section": mapped_popular_movies, "friends_activity_section": friends_activity})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/getRecommendedMovies/<movieId>', methods=['GET'])
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
        user_social_data = get_user_social_data(userId)

        return jsonify(user_social_data)
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
        UserFriend.UserId == userId,
    )
    # Query for friends where the user is the recipient
    friends_as_friend = db.session.query(User).join(UserFriend, User.Id == UserFriend.UserId).filter(
        UserFriend.FriendId == userId
    )
    # Combine the two queries using `union`
    all_friends = friends_as_user.union(friends_as_friend)

    all_users = User.query.filter(User.Id != userId).all()
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
    pending_requests = db.session.query(UserFriend).join(User, UserFriend.UserId == User.Id).filter(
        UserFriend.FriendId == userId, UserFriend.Status == 0
    )



    # for every friend request get their mutual friends count and append it to the pending requests list
    pending_requests_with_mutual_friends = []
    for pending_request in pending_requests.all():
        mutual_friends_as_user = db.session.query(User).join(UserFriend, User.Id == UserFriend.FriendId).filter(
            UserFriend.UserId == pending_request.UserId, UserFriend.Status == 1
        ).count()
        mutual_friends_as_friend = db.session.query(User).join(UserFriend, User.Id == UserFriend.UserId).filter(
            UserFriend.FriendId == pending_request.UserId, UserFriend.Status == 1
        ).count()
        user = User.query.filter(User.Id == pending_request.UserId).first()
        pending_requests_with_mutual_friends.append({"id": pending_request.Id, "name": user.Login, "mutualFriends": mutual_friends_as_user + mutual_friends_as_friend})
    
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
@app.route('/getAdvancedMovieDetails/<movieId>', methods=['GET'])
def get_advanced_movie_details(movieId: str):
    reviews = Review.query.where(Review.MovieId == movieId).order_by(Review.Date.desc()).all()
    return [{"reviewer": review.User.Login, "comment": review.Comment, "rating": review.Rating, "id": review.Id} for review in reviews]



if __name__ == '__main__':
    app.run(port=5001, debug=True)
