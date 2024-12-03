import unittest
import requests

class TestRaft(unittest.TestCase):

    def test_vote_request(self):
        response = requests.post("http://localhost:5001/request_vote", json={"term": 1, "candidate_id": "http://localhost:5001"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("vote_granted", response.json())

    def test_append_entries(self):
        response = requests.post("http://localhost:5001/append_entries", json={"term": 1, "leader_id": "http://localhost:5001"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())

    def test_start_election(self):
        response = requests.post("http://localhost:5001/start_election")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Election started")

    def test_simulate_failure(self):
        response = requests.post("http://localhost:5000/simulate_failure", json={"node": "http://localhost:5001", "duration": 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Failure simulation started")

if __name__ == "__main__":
    unittest.main()