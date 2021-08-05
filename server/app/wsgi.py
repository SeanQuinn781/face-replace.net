from app import app
from flask import Flask

if __name__ == "__main__":
    # Session(app)
    app.debug = True
    app.config["SESSION_TYPE"] = "filesystem"
    # session.init_app(app)
    print("app is ", app)
    app.run(host="0.0.0.0")
    # app.run()
