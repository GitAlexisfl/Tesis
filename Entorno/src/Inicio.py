from flask import Flask
from Paciente import appP
from Citas import appC
from flask_cors import CORS

app = Flask(__name__)

CORS(appP)
CORS(appC)
app.register_blueprint(appP)
app.register_blueprint(appC)


if __name__ == '__main__':
    app.run(debug=True)
#ruta http://127.0.0.1:5000