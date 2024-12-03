import threading
import time
import random
import requests
from flask import Flask, request, jsonify
from utils import log_message

class RaftNode:
    def __init__(self, node_id, nodes):
        self.node_id = node_id
        self.nodes = nodes
        self.state = {
            "term": 0,
            "voted_for": None,
            "logs": [],
            "commit_index": 0,
            "last_applied": 0,
            "role": "follower",
            "leader_id": None,
        }
        self.votes_received = 0
        self.election_timeout = random.uniform(2, 3)  # Aumentar intervalo de timeout de eleição
        self.heartbeat_interval = 0.5  # Intervalo de heartbeats
        self.last_heartbeat = time.time()
        self.running = True

        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/request_vote', methods=['POST'])
        def request_vote():
            data = request.get_json()
            if data['term'] > self.state['term']:
                self.state['term'] = data['term']
                self.state['voted_for'] = data['candidate_id']
                self.state['role'] = 'follower'
                log_message(f"Node {self.node_id} voted for node {data['candidate_id']} in term {data['term']}")
                return jsonify({"vote_granted": True, "term": self.state['term']})
            elif data['term'] == self.state['term'] and (self.state['voted_for'] is None or self.state['voted_for'] == data['candidate_id']):
                self.state['voted_for'] = data['candidate_id']
                log_message(f"Node {self.node_id} voted for node {data['candidate_id']} in term {data['term']}")
                return jsonify({"vote_granted": True, "term": self.state['term']})
            else:
                return jsonify({"vote_granted": False, "term": self.state['term']})

        @self.app.route('/append_entries', methods=['POST'])
        def append_entries():
            data = request.get_json()
            if data['term'] >= self.state['term']:
                self.state['term'] = data['term']
                self.state['leader_id'] = data['leader_id']
                self.state['role'] = 'follower'
                self.last_heartbeat = time.time()
                log_message(f"Node {self.node_id} received append entries from leader {data['leader_id']} in term {data['term']}")
                return jsonify({"success": True, "term": self.state['term']})
            else:
                return jsonify({"success": False, "term": self.state['term']})

        @self.app.route('/start_election', methods=['POST'])
        def start_election_route():
            self.start_election()
            return "Election started", 200

        @self.app.route('/status', methods=['GET'])
        def status():
            return jsonify(self.state), 200

        @self.app.route('/simulate_failure', methods=['POST'])
        def simulate_failure_route():
            data = request.get_json()
            duration = data['duration']
            threading.Thread(target=self.simulate_failure, args=(duration,)).start()
            return "Failure simulation started", 200

    def check_node_availability(self, node):
        try:
            response = requests.get(f"{node}/status")
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            return False
        return False

    def start_election(self):
        if self.state['role'] == 'leader':
            return  # O líder não deve iniciar uma nova eleição

        self.state['term'] += 1
        self.state['voted_for'] = self.node_id
        self.votes_received = 1
        self.state['role'] = 'candidate'
        log_message(f"Node {self.node_id} started election for term {self.state['term']}")

        for node in self.nodes:
            if node != self.node_id and self.check_node_availability(node):
                try:
                    response = requests.post(f"{node}/request_vote", json={"term": self.state['term'], "candidate_id": self.node_id})
                    if response.json().get('vote_granted'):
                        self.votes_received += 1
                        log_message(f"Node {self.node_id} received vote from {node} for term {self.state['term']}")
                        if self.votes_received > len(self.nodes) // 2:
                            self.state['role'] = 'leader'
                            self.state['leader_id'] = self.node_id
                            log_message(f"Node {self.node_id} is elected as leader for term {self.state['term']}")
                            self.send_heartbeats()
                            return
                except requests.exceptions.RequestException as e:
                    log_message(f"Error sending vote request to {node}: {e}")

    def send_heartbeats(self):
        log_message(f"Node {self.node_id} sending heartbeats")
        while self.state['role'] == 'leader' and self.running:
            for node in self.nodes:
                if node != self.node_id and self.check_node_availability(node):
                    try:
                        response = requests.post(f"{node}/append_entries", json={"term": self.state['term'], "leader_id": self.node_id})
                        if response.json().get('term') > self.state['term']:
                            self.state['term'] = response.json().get('term')
                            self.state['role'] = 'follower'
                            log_message(f"Node {self.node_id} reverted to follower for term {self.state['term']}")
                            return
                    except requests.exceptions.RequestException as e:
                        log_message(f"Error sending append entries to {node}: {e}")
            time.sleep(self.heartbeat_interval)

    def simulate_failure(self, duration):
        log_message(f"Node {self.node_id} simulating failure for {duration} seconds")
        self.running = False
        time.sleep(duration)
        self.running = True
        log_message(f"Node {self.node_id} recovered from failure")

    def run(self):
        threading.Thread(target=lambda: self.app.run(port=int(self.node_id.split(":")[-1]))).start()
        time.sleep(1)  # Give the server time to start

        while True:
            if not self.running:
                time.sleep(1)
                continue

            if self.state['role'] == 'follower':
                if time.time() - self.last_heartbeat > self.election_timeout:
                    self.start_election()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python raft.py <node_id>")
        sys.exit(1)
    
    nodes = ["http://localhost:5001", "http://localhost:5002", "http://localhost:5003"]
    node_id = sys.argv[1]
    node = RaftNode(node_id, nodes)
    node.run()