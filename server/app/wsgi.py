# wsgi entrypoint for gunicorn
# https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04
from app import app
from flask import Flask

if __name__ == "__main__":
    # Session(app)
    app.debug = True
    app.config["SESSION_TYPE"] = "filesystem"
    # session.init_app(app)
    # uncommented this 8-6-21
    # app.run(host="0.0.0.0")
    app.run()
