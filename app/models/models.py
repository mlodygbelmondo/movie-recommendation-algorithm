# coding: utf-8
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Table, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from extensions import db

Base = db.Model
metadata = Base.metadata

class Country(Base):
    __tablename__ = 'Countries'

    Id = Column(UUID, primary_key=True)
    Name = Column(String(200), nullable=False)

    Movies = relationship('Movie', secondary='MovieCountries')


class Person(Base):
    __tablename__ = 'People'

    Id = Column(UUID, primary_key=True)
    FirstName = Column(String(50), nullable=False)
    LastName = Column(String(50), nullable=False)
    BirthDate = Column(Date, nullable=False)
    Biography = Column(String(500), nullable=False)
    Image = Column(Text)


class UserFriend(Base):
    __tablename__ = 'UserFriends'

    Id = Column(UUID, primary_key=True)
    UserId = Column(UUID, nullable=False)
    FriendId = Column(UUID, nullable=False)
    Status = Column(Integer, nullable=False)


class User(Base):
    __tablename__ = 'Users'

    Id = Column(UUID, primary_key=True)
    Login = Column(String(50), nullable=False)
    Password = Column(String(250), nullable=False)
    Email = Column(String(50), nullable=False)


class EFMigrationsHistory(Base):
    __tablename__ = '__EFMigrationsHistory'

    MigrationId = Column(String(150), primary_key=True)
    ProductVersion = Column(String(32), nullable=False)


class Movie(Base):
    __tablename__ = 'Movies'

    Id = Column(UUID, primary_key=True)
    Title = Column(String(200), nullable=False)
    Description = Column(String(2000), nullable=False)
    Genre = Column(Integer, nullable=False)
    ReleaseDate = Column(Date, nullable=False)
    BoxOffice = Column(Integer, nullable=False)
    Duration = Column(Integer, nullable=False)
    Image = Column(Text)
    UserId = Column(ForeignKey('Users.Id'), index=True)
    UserId1 = Column(ForeignKey('Users.Id'), index=True)
    Popularity = Column(Numeric, nullable=False, server_default=text("0.0"))
    Tmdb_Id = Column(Integer, nullable=False, server_default=text("0"))

    User = relationship('User', primaryjoin='Movie.UserId == User.Id')
    User1 = relationship('User', primaryjoin='Movie.UserId1 == User.Id')


class FavoriteMovie(Base):
    __tablename__ = 'FavoriteMovies'

    Id = Column(UUID, primary_key=True)
    MovieId = Column(ForeignKey('Movies.Id', ondelete='CASCADE'), nullable=False, index=True)
    UserId = Column(ForeignKey('Users.Id', ondelete='CASCADE'), nullable=False, index=True)
    CreatedAt = Column(DateTime(True), nullable=False, server_default=text("'-infinity'::timestamp with time zone"))
    LastModifiedAt = Column(DateTime(True))

    Movie = relationship('Movie')
    User = relationship('User')


t_MovieCountries = Table(
    'MovieCountries', metadata,
    Column('CountryId', ForeignKey('Countries.Id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True),
    Column('MovieId', ForeignKey('Movies.Id', ondelete='CASCADE'), primary_key=True, nullable=False)
)


class Review(Base):
    __tablename__ = 'Reviews'

    MovieId = Column(ForeignKey('Movies.Id', ondelete='CASCADE'), primary_key=True, nullable=False)
    UserId = Column(ForeignKey('Users.Id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    Id = Column(UUID, nullable=False)
    Comment = Column(String(500), nullable=False)
    Rating = Column(Integer, nullable=False)
    CreatedAt = Column(DateTime(True), nullable=False, server_default=text("'-infinity'::timestamp with time zone"))
    LastModifiedAt = Column(DateTime(True))

    Movie = relationship('Movie')
    User = relationship('User')


class Role(Base):
    __tablename__ = 'Roles'

    Id = Column(UUID, primary_key=True)
    PersonId = Column(ForeignKey('People.Id', ondelete='CASCADE'), nullable=False, index=True)
    MovieId = Column(ForeignKey('Movies.Id', ondelete='CASCADE'), nullable=False, index=True)
    MovieProductionRole = Column(Integer, nullable=False)
    Character = Column(String(50))

    Movie = relationship('Movie')
    Person = relationship('Person')


class WatchLaterMovie(Base):
    __tablename__ = 'WatchLaterMovies'

    Id = Column(UUID, primary_key=True)
    MovieId = Column(ForeignKey('Movies.Id', ondelete='CASCADE'), nullable=False, index=True)
    UserId = Column(ForeignKey('Users.Id', ondelete='CASCADE'), nullable=False, index=True)
    CreatedAt = Column(DateTime(True), nullable=False, server_default=text("'-infinity'::timestamp with time zone"))
    LastModifiedAt = Column(DateTime(True))

    Movie = relationship('Movie')
    User = relationship('User')


class RoleReview(Base):
    __tablename__ = 'RoleReviews'

    Id = Column(UUID, primary_key=True)
    RoleId = Column(ForeignKey('Roles.Id', ondelete='CASCADE'), nullable=False, index=True)
    UserId = Column(ForeignKey('Users.Id', ondelete='CASCADE'), nullable=False, index=True)
    Rating = Column(Integer, nullable=False)
    CreatedAt = Column(DateTime(True), nullable=False, server_default=text("'-infinity'::timestamp with time zone"))
    LastModifiedAt = Column(DateTime(True))

    Role = relationship('Role')
    User = relationship('User')
