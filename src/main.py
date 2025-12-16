import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

room_list = ["bedroom1", "bedroom2", "celar", "garage", "kitchen", "livingroom", "office"]


@app.route("/", methods=["POST"])
def parse_request():
    """
    Parse incoming JSON request and log temperature and humidity data.

    This function extracts room name, temperature, and humidity from a JSON request,
    validates the room name against an allowed list, and appends the data to a
    dated log file specific to that room.

    Expected JSON format:
        {
            "room": str,      # Name of the room
            "temp": str,      # Temperature value
            "hydro": str      # Humidity value
        }

    Returns:
        tuple: A tuple containing:
            - str: Empty string (message body)
            - int: HTTP status code
                - 200: Successfully logged the data
                - 500: Invalid room name or error occurred during processing

    Side Effects:
        - Writes to log file at path: /logs/{room_name}/{date}.log
        - Creates or appends to existing log file

    Note:
        - Log format: {time};{temp};{hydro}

    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return ("", 500)

        # Log file path
        now = datetime.now()
        room_name = data.get("room")

        if room_name not in room_list:
            return ("", 500)

        filepath = os.path.join("/logs", room_name, f"{now.date()}.log")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Construct the log message
        temp = str(data.get("temp", ""))
        hydro = str(data.get("hydro", ""))
        logline = f"{now.time()};{temp};{hydro}\n"

        # Write to log file
        with open(filepath, "a", encoding="utf-8") as logfile:
            logfile.write(logline)

        return ("", 200)
    except Exception:
        return ("", 500)


@app.route("/", methods=["GET"])
def extract_logs():
    """
    Extracts the latest logs for each room from log files and returns the data in JSON format.

    This function iterates through a predefined list of room names, checks for the existence of log files
    for the current date, and reads the last entry from each log file. The extracted data includes the
    last log time, temperature, and humidity for each room.

    Returns:
        tuple: A tuple containing a JSON response with the extracted log data and an HTTP status code.

    The JSON response format is:
        {
            "room_name": {
                "last_log_time": str,  # Time of last log entry (HH:MM:SS.mmmmmm) or "N/A"
                "last_temp": str,      # Temperature value or "N/A"
                "last_hydro": str      # Humidity value or "N/A"
            },
            ...
        }

    Raises:
        Exception: If there is an error while processing the log files or reading their contents.

    """
    now = datetime.now()

    json_data = {}
    for room_name in room_list:
        try:
            path = "/logs/" + room_name + "/" + str(now.date()) + ".log"

            last_log_time = "N/A"
            last_temp = "N/A"
            last_hydro = "N/A"

            if os.path.isfile(path):
                log_file = open(path, "r", encoding="utf-8")

                lines = log_file.readlines()
                if lines:
                    last_entry = lines[-1].strip().split(";")
                    last_log_time = last_entry[0]
                    last_temp = last_entry[1]
                    last_hydro = last_entry[2]

                log_file.close()

            json_data[room_name] = {
                "last_log_time": last_log_time,
                "last_temp": last_temp,
                "last_hydro": last_hydro,
            }

        except Exception:
            json_data[room_name] = {
                "last_log_time": "N/A",
                "last_temp": "N/A",
                "last_hydro": "N/A",
            }

    return jsonify(json_data), 200


if __name__ == "__main__":
    app.debug = True
    app.run(host="127.0.0.1", port=5000)
