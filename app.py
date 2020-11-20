from flask import Flask
from user import user_blueprint
from drugs import drugs_blueprint
from doctor import doctor_blueprint


app = Flask(__name__)
app.register_blueprint(user_blueprint)
app.register_blueprint(drugs_blueprint)
app.register_blueprint(doctor_blueprint)


if __name__ == '__main__':
    app.debug = True
    app.run()
