from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
import webbrowser
import threading
import tkinter as tk
import requests
import pandas as pd
import time
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables for threading
observation_thread = None
should_observe = False
schedule_data = None

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def init_db():
    with sqlite3.connect("school_bell.db") as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL
            );
        ''')


def load_schedule():
    global schedule_data
    conn = sqlite3.connect("school_bell.db")
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM schedules ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        filename = row[0]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        schedule_data = pd.read_csv(file_path)


def observe_time():
    global schedule_data, should_observe
    while should_observe:
        if schedule_data is not None:
            now = datetime.now().strftime("%H:%M")  # Adjust the format as needed
            for _, row in schedule_data.iterrows():
                if row['Time'] == now:
                    print(row['Command'])  # Replace with actual action
            time.sleep(60)  # Check every minute
        else:
            time.sleep(10)  # Wait before checking the schedule again
    print("Observation thread stopped.")


@app.route('/')
def index():

    return render_template('index.html')


@app.route("/set-schedule")
def setSchedule():

    return render_template('setSchedule.html')


@app.route('/schedule')
def schedule():
    conn = sqlite3.connect("school_bell.db")
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM schedules ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        filename = row[0]
        return redirect(url_for('display_csv', filename=filename))
    else:
        return "No schedule found", 404


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/display-csv')
def display_csv():
    conn = sqlite3.connect("school_bell.db")
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM schedules LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        filename = row[0]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        df = pd.read_csv(file_path)

        data = df.to_dict(orient='records')
        print(f"Data: {data}")
        return render_template('setSchedule.html', data=data)
    else:
        return "No schedule file uploaded", 404


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return 'File not allowed or invalid file type', 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    with sqlite3.connect("school_bell.db") as conn:
        # Clear the existing record (if any)
        conn.execute("DELETE FROM schedules")
        # Inserting the new filename
        conn.execute(
            "INSERT INTO schedules (filename) VALUES (?)", (filename,))
        conn.commit()

    return redirect(url_for('index'))


@app.route('/start-observing')
def start_observing():
    global observation_thread, should_observe
    load_schedule()

    if observation_thread is None or not observation_thread.is_alive():
        should_observe = True
        observation_thread = threading.Thread(target=observe_time, daemon=True)
        observation_thread.start()
        return jsonify({'message': 'Observation started'})
    else:
        return jsonify({'message': 'Observation already in progress'})


@app.route('/shutdown')
def shutdown():
    global should_observe
    should_observe = False  # Signal the observation thread to stop
    shutdown_function = request.environ.get('werkzeug.server.shutdown')
    if shutdown_function is None:
        raise RuntimeError('Not able to shutdown the server')
    shutdown_function()
    return 'Server shutting down...'

# Tkinter GUI


def run_flask():
    app.run(debug=True, use_reloader=False)


def start_flask():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    webbrowser.open_new('http://127.0.0.1:5000/')


def exit_app(root):
    try:
        requests.get('http://127.0.0.1:5000/shutdown')
    except Exception as e:
        print("Error shutting down Flask server: ", e)
    finally:
        root.destroy()


def create_gui():
    root = tk.Tk()
    root.title("Flask App Control")
    root.geometry("300x150")
    root.configure(bg='azure')
    icon_path = os.path.join(os.path.dirname(__file__), 'bell.ico')
    root.iconbitmap(icon_path)

    start_button = tk.Button(root, text="Start Flask",
                             command=start_flask, bg='SpringGreen2', fg='white')
    start_button.grid(row=0, column=0, padx=10, pady=10)

    start_observing_button = tk.Button(
        root, text="Start Observing", command=start_observing, bg='royal blue', fg='white')
    start_observing_button.grid(row=1, column=0, padx=10, pady=10)

    exit_button = tk.Button(root, text="Exit", command=lambda: exit_app(
        root), bg='firebrick3', fg='white')
    exit_button.grid(row=2, column=0, padx=10, pady=10)

    root.mainloop()


if __name__ == '__main__':
    init_db()
    create_gui()
