from database import db


def init_db(db_uri, app):
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    db.init_app(app)

    with app.app_context():
        db.create_all()
