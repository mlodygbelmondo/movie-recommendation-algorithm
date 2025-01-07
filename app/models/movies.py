from extensions import db

class Movies(db.Model):
    __tablename__ = 'Movies'
    Id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(50), nullable=False)
    Description = db.Column(db.String(999), nullable=False)
    ReleaseDate = db.Column(db.Integer, nullable=False)
    Duration = db.Column(db.Integer, nullable=False)
    Image = db.Column(db.String(100), nullable=False)
    BoxOffice = db.Column(db.Float, nullable=False)
    Popularity = db.Column(db.Float, nullable=False)
    Tmdb_Id = db.Column(db.Integer, nullable=False)
    Genre = db.Column(db.Integer, nullable=False)