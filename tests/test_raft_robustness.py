import time
import requests
import subprocess
import unittest

class TestRaftRobustness(unittest.TestCase):

    def setUp(self):
        # Start nodes
        self.nodes = [
            subprocess.Popen(["python", "raft.py", "http://localhost:5001"]),
            subprocess.Popen(["python", "raft.py", "http://localhost:5002"]),
            subprocess.Popen(["python", "raft.py", "http://localhost:5003"])
        ]
        time.sleep(5)  # Give nodes time to start

    def tearDown(self):
        # Terminate nodes
        for node in self.nodes:
            node.terminate()

    def test_recovery_from_failure(self):
        # Start election and wait for leader
        requests.post("http://localhost:5001/start_election")
        time.sleep(3)
        
        # Simulate failure of leader
        self.nodes[0].terminate()
        time.sleep(3)
        
        # Verify new election
        requests.post("http://localhost:5002/start_election")
        time.sleep(3)
        
        # Check if a new leader is elected
        response = requests.get("http://localhost:5002/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['role'], 'leader')

if __name__ == "__main__":
    unittest.main()