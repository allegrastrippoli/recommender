from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin
from repository import select_random_movies, select_user, insert_rating
from recommender import Recommender

class ConfigClass(object):
    """ Flask application config """

    SECRET_KEY = 'yolo'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.sqlite'    
    SQLALCHEMY_TRACK_MODIFICATIONS = False   
 
    USER_APP_NAME = "Recommender"     
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

    app.recommender = Recommender()

    # @app.route('/refresh_movies')
    # @login_required
    # def refresh_movies():
    #     selected_movies = request.form.getlist('selected_movies')
    #     movies = select_random_movies()
    #     return render_template("start.html", selected_movies=selected_movies, movies=movies)

    @app.route('/get_recommendations', methods=['POST'])
    @login_required    
    def get_recommendations():
        if request.method == "POST":
            selected_movies= request.form.getlist('selected_movies')
            insert_rating(int(current_user.id), selected_movies, "5.0")
            print('Done inserting user ratings.')
            recs = app.recommender.get_top_k_recommendations(str(current_user.id))
            return render_template("recommendations.html", recs=recs)
        

    @app.route('/')
    @login_required    
    def init():
        id = current_user.id
        # if select_user(int(id)):
        #     recs = app.recommender.get_top_k_recommendations(str(id))
        #     return render_template("recommendations.html", recs=recs)
        # else:
        #     movies = select_random_movies()
        #     return render_template("start.html", movies=movies)
        movies = select_random_movies()
        return render_template("start.html", movies=movies)

    return app


if __name__=='__main__':

    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
