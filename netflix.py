"""
Netflix catalogue API implemented using Google Cloud Endpoints.
Author: Abhishek Chatterjee
Date: Jan 6, 2016

Uses:
- The Open Movie Database (OMDb) API for IMDb: http://www.omdbapi.com/
- The Netflix Roulette API for Netflix for now.
"""

import endpoints
import json
from protorpc import messages
from protorpc import message_types
from protorpc import remote
import urllib2
from google.appengine.api import urlfetch

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
        movie = self.getMovieFromId("tt1285016")
        return MovieCollection(movies_list=[movie])

    """
    Lists best parodies. This reads from a static (and, it must be conceded, subjective)
    list of the top 50 parodies on IMDb, and returns movies that are available to stream
    on Netflix.
    """
    @endpoints.method(message_types.VoidMessage, MovieCollection,
        path="movies/lists/best_parodies", http_method="GET",
        name="movies.listparodies")
    def parodies_list(self, request):
        movies = self.readList("lists/parodies_list.txt")
        return MovieCollection(movies_list=movies)

    """
    Creates a Movie object using an IMDb id.
    """
    def getMovieFromId(self, imdbId):
        response = urllib2.urlopen("http://www.omdbapi.com/?i="+imdbId)
        data = json.load(response)
        movie = Movie(name=data["Title"],
            media_type=data["Type"],
            genre=data["Genre"].split(", "),
            year=data["Year"],
            plot=data["Plot"],
            rating=data["imdbRating"])
        return movie

    """
    Gets the name of a movie from its IMDb id.
    """
    def getMovieNameFromId(self, imdbId):
        response = urllib2.urlopen("http://www.omdbapi.com/?i="+imdbId)
        data = json.load(response)
        return data["Title"]

    """
    Creates a list of Movies from a file containing IMDb IDs. A movie is added
    to the list if it also exists in the Netflix catalogue.
    """
    def readList(self, pathname):
        f = open(pathname, "r")
        movies = []
        for line in f:
            name = self.getMovieNameFromId(line)
            if self.isOnNetflix(name):
                movies.append(self.getMovieFromId(line))
        return movies

    """
    Returns true, if the movie is on Netflix...
    """
    def isOnNetflix(self, name):
        try:
            print "http://netflixroulette.net/api/api.php?title="+name.encode("utf8").replace(" ", "%20")
            response = urlfetch.fetch("http://netflixroulette.net/api/api.php?title="+name.replace(" ", "%20"))
            print "Code: " + str(response.status_code)
            return response.status_code == 200
        except (urlfetch.InvalidURLError, urlfetch.DownloadError):
            return False

APPLICATION = endpoints.api_server([NetflixApi])