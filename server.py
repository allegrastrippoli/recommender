from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin
from repository import select_random_movies, check_if_user_has_ratings, insert_rating, select_movie_from_title, select_random_movies_not_rated
from recommender import get_top_n_rec

class ConfigClass(object):
    """ Flask application config """

    SECRET_KEY = 'yolo'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.sqlite'    
    SQLALCHEMY_TRACK_MODIFICATIONS = False   
 
    USER_APP_NAME = ""
    USER_ENABLE_EMAIL = False     
    USER_ENABLE_USERNAME = True   
    USER_REQUIRE_RETYPE_PASSWORD = False  


def create_app():
    """ Flask application factory """
    
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    db = SQLAlchemy(app)

    # NB: Make sure to add flask_user UserMixin !!!
    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

        # The collation='NOCASE' is required to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
        username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
        password = db.Column(db.String(255), nullable=False, server_default='')
        email_confirmed_at = db.Column(db.DateTime())

        # User information
        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

    with app.app_context():
        db.create_all()

    user_manager = UserManager(app, db, User)
    
    def add_selected_movies():
           selected_movies = request.form.getlist('selected_movies')
           if len(selected_movies) > 0:
            if 'selected_movies' in session:  
                    existing_movies = session['selected_movies']
                    session['selected_movies'] = list(set(existing_movies + selected_movies))
                    print(f'Adding {(session['selected_movies'])} to existing session...')
            else:
                    session['selected_movies'] = selected_movies
                    print(f'Adding {(session['selected_movies'])} to existing session...')
           else:
                session['selected_movies'] = []
                return redirect(url_for('init'))

    @app.route('/shuffle_recommend', methods=['POST'])
    @login_required
    def shuffle_or_recommend():
        threshold = 3
        action = request.form.get('action')
        
        if action == 'get_recommendations':
            if request.method == "POST":
                add_selected_movies()
                if len(session['selected_movies']) >= threshold or check_if_user_has_ratings(int(current_user.id)):
                    selected_movies= session['selected_movies']
                    insert_rating(int(current_user.id), selected_movies)
                    print('Done inserting user ratings.')
                    titles = get_top_n_rec(str(current_user.id))
                    recs = select_movie_from_title(titles)
                    session.pop('selected_movies', None) 
                    return render_template("recommendations.html", recs=recs)
                else:    
                    flash(f'You need {threshold-len(session['selected_movies'])} movies to continue...')
                    return redirect(url_for('init'))

            else:
                return "Invalid request", 400
        
        elif action == 'shuffle':
            print('Shuffling...')
            if request.method == 'POST':
                add_selected_movies()
            
            movies = select_random_movies_not_rated(int(current_user.id))
            selected_movies = session.get('selected_movies', [])
            return render_template("start.html", movies=movies, selected_movies=selected_movies)

        return "Invalid action", 40
    
    @app.route('/recommendations', methods=['GET', 'POST'])  
    @login_required  
    def get_recommendations():
        id = current_user.id
        if check_if_user_has_ratings(int(id)):
            titles = get_top_n_rec(str(id))
            recs = select_movie_from_title(titles)
            return render_template("recommendations.html", recs=recs)
        else:
            movies = select_random_movies_not_rated(int(current_user.id))
            return render_template("start.html", movies=movies)

    @app.route('/')  
    @login_required  
    def init():
        movies = select_random_movies_not_rated(int(current_user.id))
        return render_template("start.html", movies=movies)

    return app


if __name__=='__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
