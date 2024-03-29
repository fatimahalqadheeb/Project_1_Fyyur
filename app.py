#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate 
import sys
from sqlalchemy import Date, cast
from datetime import date, datetime
import enum
from sqlalchemy import String, Integer, ARRAY,  func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
#----------------------------------------------------------------------------#
# Migration.
#----------------------------------------------------------------------------#
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(250))
    show = db.relationship('Show', backref='venue')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String()))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(250))
    show = db.relationship('Show', backref='artist')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)
app.jinja_env.filters['datetime'] = format_datetime
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/')
def index():
  return render_template('pages/home.html')
#  Genres
#----------------------------------------------------------------------------#
# @app.route('/artists/create', methods=['GET'])
# def list_genres():
#   genres = Genre.query.all()
#   return render_template('forms/new_artist.html', genres=genres)
#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #  num_shows should be aggregated based on number of upcoming shows per venue.
  # check how you are passing your data, into which jinja part?
  venue_group_by_city= Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []
  dateToday = datetime.now()
  for result_venues in venue_group_by_city:
    venues = Venue.query.filter_by(city= result_venues.city).filter_by(state = result_venues.state).all()
    venues_shows = []
    for x in venues:
      if (result_venues.city == x.city) and (result_venues.state == x.state): 
        shows = Show.query.filter_by(venue_id =x.id).all()
        num = 0
        for show in shows:
          if show.start_time >= dateToday:
            num =+ 1
      venues_shows.append({
              "id": x.id,
              "name": x.name,
              "upcoming_show": num
          })
    data.append({
          "city" : result_venues.city,
          "state" : result_venues.state, 
           "venues" : venues_shows
          })
  return render_template('pages/venues.html', areas=data)
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')
  value = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  response = {
    "count": len(value),
    "data": value
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  past_shows =[]
  upcoming_shows = []
  dateToday = datetime.now()
  select_venue_by_id=Venue.query.get(venue_id)
  shows=Show.query.filter_by(venue_id=venue_id).all()
  for show in shows:
    if show.start_time >= dateToday:
      upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link":Artist.query.filter_by(id=show.artist_id).first().image_link ,
      "start_time": show.start_time })
    else:
      past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link":Artist.query.filter_by(id=show.artist_id).first().image_link ,
      "start_time": show.start_time })
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = {
    "id": select_venue_by_id.id,
    "name": select_venue_by_id.name,
    "genres": select_venue_by_id.genres ,
    "address": select_venue_by_id.address,
    "city": select_venue_by_id.city,
    "state": select_venue_by_id.state,
    "phone": select_venue_by_id.phone,
    "website": select_venue_by_id.website,
    "facebook_link": select_venue_by_id.facebook_link,
    "seeking_talent": True,
    "seeking_description": select_venue_by_id.seeking_description,
    "image_link": select_venue_by_id.image_link ,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name = request.form.get('name', '')
    city=request.form.get('city', '')
    state=request.form.get('state', '')
    address=request.form.get('address', '')
    phone=request.form.get('phone', '')
    image_link=request.form.get('image_link', '')
    genres= request.form.getlist('genres',)
    facebook_link=request.form.get('facebook_link', '')
    venue = Venue(name=name, city=city, state=state, address=address, 
                phone=phone, image_link=image_link, genres=genres,
                facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    error = True
    db.session.rollback()
    flash('An error occurred.'+ name +' Venue  could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
   venue = Venue.query.get(venue_id) 
   db.session.delete(venue)
   db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term','')
  value = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  response={
    "count": len(value),
    "data": value
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  past_shows = []
  upcoming_shows = []
  dateToday= datetime.now()
  shows = Show.query.filter_by(artist_id=artist_id).all()
  select_artist_by_id = Artist.query.get(artist_id)
  for show in shows:
    if show.start_time >= dateToday:
      upcoming_shows.append({
        "venue_id" : show.venue_id,
        "venue_name" : Venue.query.filter_by(id=show.venue_id).first().name,
        "venue_image_link" : Venue.query.filter_by(id=show.venue_id).first().image_link ,
        "start_time": show.start_time
        })
    else:
      past_shows.append({
      "venue_id" : show.venue_id,
      "venue_name" : Venue.query.filter_by(id=show.venue_id).first().name,
      "venue_image_link" : Venue.query.filter_by(id=show.venue_id).first().image_link ,
      "start_time": show.start_time
      })
  data = ({
    "id": select_artist_by_id.id,
    "name": select_artist_by_id.name,
    "genres": select_artist_by_id.genres,
    "city": select_artist_by_id.city,
    "state": select_artist_by_id.state,
    "phone": select_artist_by_id.phone,
    "website": select_artist_by_id.website,
    "facebook_link": select_artist_by_id.facebook_link,
    "seeking_venue": True,
    "seeking_description": select_artist_by_id.seeking_description,
    "image_link": select_artist_by_id.image_link ,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  })
  return render_template('pages/show_artist.html', artist = data)
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  artist = { 
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "image_link" :  artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try: 
    name = request.form.get('name', '')
    city=request.form.get('city', '')
    state=request.form.get('state', '')
    address=request.form.get('address', '')
    phone=request.form.get('phone', '')
    image_link=request.form.get('image_link', '')
    genres= request.form.getlist('genres',)
    facebook_link=request.form.get('facebook_link', '')
    artist = Artist.query.get(artist_id)
    artist.name = name
    artist.city = city
    artist.state = state
    artist.address = address
    artist.phone = phone
    artist.image_link = image_link
    artist.genres = genres
    artist.facebook_link = facebook_link
    db.session.commit()
    flash(' The artist information updated successfully')
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.facebook_link.data = venue.facebook_link
  venue = { 
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "facebook_link": venue.facebook_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try: 
    name = request.form.get('name', '')
    city=request.form.get('city', '')
    state=request.form.get('state', '')
    address=request.form.get('address', '')
    phone=request.form.get('phone', '')
    genres=request.form.get('genres', '')
    facebook_link=request.form.get('facebook_link', '')
    venue = Venue.query.get(venue_id)
    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.facebook_link = facebook_link
    db.session.commit()
    flash(' The venue information updated successfully')
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))
#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name=request.form.get('name', '')
    city=request.form.get('city', '')
    state=request.form.get('state', '')
    phone=request.form.get('phone', '')
    image_link=request.form.get('image_link', '')
    genres=request.form.getlist('genres')
    facebook_link=request.form.get('facebook_link', '')
    artist=Artist(name=name, city=city, state=state, phone=phone, 
                  image_link=image_link, genres=genres, facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + name + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')
#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  select_all_show = Show.query.all()
  for shows in select_all_show:
    select_by_venue_id= Venue.query.get(shows.venue_id)
    select_by_artist_id= Artist.query.get(shows.artist_id)
    data.append({
    'id' : shows.venue_id,
    'venue_name' : select_by_venue_id.name,
    'artist_id' : shows.venue_id,
    'artist_name' : select_by_artist_id.name,
    'artist_image_link' : select_by_artist_id.image_link,
    'start_time' : shows.start_time
  })
  return render_template('pages/shows.html', shows=data)
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error= False
  try:
    artist_id=request.form.get('artist_id')
    venue_id=request.form.get('venue_id')
    start_time=request.form.get('start_time')
    show=Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist  could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#
# Default port:
if __name__ == '__main__':
    app.run()
# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''