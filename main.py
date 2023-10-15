from flask import Flask

from blueprints.hospitals import hospitals_blueprint
from blueprints.physicians import physicians_blueprint

app = Flask(__name__)
app.register_blueprint(hospitals_blueprint, url_prefix='/hospitals')
app.register_blueprint(physicians_blueprint, url_prefix='/physicians')

if __name__ == '__main__':
    app.run(debug=True)
