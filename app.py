from flask import Flask, render_template, request, jsonify
import random
import time
from threading import Thread
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///experiment_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model for saving data


class ExperimentData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    button = db.Column(db.String(10))
    points = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Create the database
with app.app_context():
    db.create_all()

# Experiment variables
bank = 0
vi_schedules = [30, 60]  # VI 30 s, VI 60 s
current_vi = vi_schedules[0]
last_reward_time = [0, 0]  # For button A and B


def update_bank(button):
    global bank
    bank += 5
    db.session.add(ExperimentData(button=button, points=5))
    db.session.commit()


def check_vi(button_index):
    global last_reward_time, current_vi
    now = time.time()
    if now - last_reward_time[button_index] >= random.expovariate(1.0 / current_vi):
        last_reward_time[button_index] = now
        return True
    return False

# Background thread to change VI schedule after 3 minutes


def schedule_changer():
    global current_vi
    time.sleep(180)  # 3 minutes
    current_vi = vi_schedules[1]


Thread(target=schedule_changer, daemon=True).start()


@app.route('/')
def index():
    return render_template('index.html', bank=bank)


@app.route('/press/<button>', methods=['POST'])
def press_button(button):
    button_index = 0 if button == 'A' else 1
    if check_vi(button_index):
        update_bank(button)
        return jsonify(success=True, bank=bank)
    return jsonify(success=False, bank=bank)


if __name__ == '__main__':
    app.run(debug=True)
