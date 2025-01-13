import pickle
from extensions import db
from models.models import User, UserFriend, FavoriteMovie, Review, Movie, WatchLaterMovie
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

def get_newest_liked_movie(last_favorite_movie, last_highly_rated_movie):
    match [last_favorite_movie, last_highly_rated_movie]:
        case (None, None):
            return None
        case (None, _):
            return last_highly_rated_movie.Movie
        case (_, None):
            return last_favorite_movie.Movie
        case (_, _):
            return last_favorite_movie.Movie if last_favorite_movie.CreatedAt > last_highly_rated_movie.CreatedAt else last_highly_rated_movie.Movie
        

def get_user_friends(userId):
    # Query for friends where the user is the requester
    friends_as_user = db.session.query(User).join(UserFriend, User.Id == UserFriend.FriendId).filter(
        UserFriend.UserId == userId, UserFriend.Status == 1
    )
    # Query for friends where the user is the recipient
    friends_as_friend = db.session.query(User).join(UserFriend, User.Id == UserFriend.UserId).filter(
        UserFriend.FriendId == userId, UserFriend.Status == 1
    )
     # Combine the two queries using `union`
    return friends_as_user.union(friends_as_friend)

def get_user_social_data(userId):
    friends = get_user_friends(userId).all()

    friends_activities = [
        activity
        for f in friends
        for activity in (
            [{'movie': map_movie(fm.Movie), 'date': fm.CreatedAt, 'friend_name': f.Login, "action": "Dodał(a) do Ulubionych"} for fm in FavoriteMovie.query.filter(FavoriteMovie.UserId == f.Id).limit(20).all()] +
            [{'movie': map_movie(r.Movie), 'date': r.CreatedAt, 'friend_name': f.Login, "action": "Zostawił(a) Recenzję"} for r in Review.query.filter(Review.UserId == f.Id, Review.Comment is not None).limit(20).all()] +
            [{'movie': map_movie(r.Movie), 'date': r.CreatedAt, 'friend_name': f.Login, "action": "Obejrzał(a)"} for r in Review.query.filter(Review.UserId == f.Id, Review.Comment is None).limit(20).all()] +
            [{'movie': map_movie(wm.Movie), 'date': wm.CreatedAt, 'friend_name': f.Login, "action": "Dodał(a) do Do Obejrzenia"} for wm in WatchLaterMovie.query.filter(WatchLaterMovie.UserId == f.Id).limit(20).all()]
        )
    ]

    friends_activities.sort(key=lambda x: x['date'], reverse=True)

    return friends_activities