from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin
# from waitress import serve 


class ConfigClass(object):
    """ Flask application config """

    SECRET_KEY = '123456789yolo'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quick start_app.sqlite'    
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

    @app.route('/')
    def home_page():
        return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>Home page</h2>
                <p><a href={{ url_for('user.register') }}>Register</a></p>
                <p><a href={{ url_for('user.login') }}>Sign in</a></p>
                <p><a href={{ url_for('home_page') }}>Home page</a></p>
                <p><a href={{ url_for('member_page') }}>Member page</a></p>
                <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
            {% endblock %}
            """)

    @app.route('/members')
    @login_required    
    def member_page():
        return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>Members page</h2>
                <p><a href={{ url_for('user.register') }}>Register</a></p>
                <p><a href={{ url_for('user.login') }}>Sign in</a></p>
                <p><a href={{ url_for('home_page') }}>Home page</a></p>
                <p><a href={{ url_for('member_page') }}>Member page</a></p>
                <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
            {% endblock %}
            """)

    return app


if __name__=='__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
