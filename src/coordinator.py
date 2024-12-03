import requests
import threading
import time
from flask import Flask, request, jsonify
from utils import log_message

app = Flask(__name__)

# Lista de nós no sistema distribuído
nodes = ["http://localhost:5001", "http://localhost:5002", "http://localhost:5003"]

@app.route('/start_election', methods=['POST'])
def start_election():
    log_message("Coordinator: Starting election")
    for node in nodes:
        response = requests.post(f"{node}/start_election")
        log_message(f"Coordinator: Election request sent to {node}, response: {response.text}")
    return "Election started", 200

@app.route('/status', methods=['GET'])
def status():
    status = {}
    for node in nodes:
        try:
            response = requests.get(f"{node}/status")
            status[node] = response.json()
        except requests.exceptions.RequestException as e:
            status[node] = f"Error: {e}"
    return jsonify(status), 200

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(port=5000)).start()
    time.sleep(1)  # Give the server time to start
    # Optionally, start the election automatically
    requests.post("http://localhost:5000/start_election")