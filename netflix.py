"""
Netflix catalogue API implemented using Google Cloud Endpoints.
Author: Abhishek Chatterjee
Date: Jan 6, 2016

Uses:
- The Open Movie Database (OMDb) API for IMDb: http://www.omdbapi.com/
"""

import endpoints
import json
from protorpc import messages
from protorpc import message_types
from protorpc import remote
import urllib2

package = "Netflix"

class Genre(messages.Message):
    genre_raw = messages.StringField(1)

class Movie(messages.Message):
    name = messages.StringField(1, required=True)
    media_type = messages.StringField(2)
    genre = messages.StringField(3, repeated=True)
    year = messages.StringField(4)
    plot = messages.StringField(5)
    rating = messages.StringField(6)

class MovieCollection(messages.Message):
    movies_list = messages.MessageField(Movie, 1, repeated=True)

@endpoints.api(name="netflix", version="v1")
class NetflixApi(remote.Service):
    """
    local path = 'http://localhost:8080/_ah/api/netflix/v1/movies'

    Testing OMDb api
    """
    @endpoints.method(message_types.VoidMessage, MovieCollection,
        path="movies", http_method="GET",
        name="movies.listmovies")
    def movies_list(self, request):
        #imdb id = tt1285016
        response = urllib2.urlopen("http://www.omdbapi.com/?i=tt1285016")
        data = json.load(response)
        movie = Movie(name=data["Title"],
            media_type=data["Type"],
            genre=data["Genre"].split(", "),
            year=data["Year"],
            plot=data["Plot"],
            rating=data["imdbRating"])
        return MovieCollection(movies_list=[movie, movie])

APPLICATION = endpoints.api_server([NetflixApi])