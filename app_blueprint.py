from flask import Blueprint
from flask import render_template

app_blueprint = Blueprint('app_blueprint', __name__)


@app_blueprint.route('/')
def index():

    return render_template('index.html')


@app_blueprint.route("/set-schedule")
def setSchedule():

    return render_template()
