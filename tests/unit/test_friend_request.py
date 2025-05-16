import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datetime import date
from Fittrack import create_app, db
from Fittrack.models import User, FriendRequest
from werkzeug.security import generate_password_hash
from Fittrack.config import TestConfig

class FriendRequestTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig) 
        self.client = self.app.test_client()

        

        with self.app.app_context():
            db.create_all()
            user1 = User(
                username='alice',
                email='alice@example.com',
                hashed_password=generate_password_hash('Password123!'),
                is_profile_complete=True,
                birthday=date(1990, 1, 1),
                age=34,
                gender='Female',
                height=165,
                current_weight=60,
                target_weight=55,
                target_weight_time_days=30,
                target_exercise_time_per_week=150,
                target_exercise_timeframe_days=60,
                avatar='default.png'
            )
            user2 = User(
                username='bob',
                email='bob@example.com',
                hashed_password=generate_password_hash('Password123!'),
                is_profile_complete=True,
                birthday=date(1992, 1, 1),
                age=32,
                gender='Male',
                height=180,
                current_weight=80,
                target_weight=75,
                target_weight_time_days=60,
                target_exercise_time_per_week=200,
                target_exercise_timeframe_days=90,
                avatar='default.png'
            )
            db.session.add_all([user1, user2])
            db.session.commit()
            self.alice_id = user1.user_id
            self.bob_id = user2.user_id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_send_friend_request(self):
        with self.app.app_context():
            request = FriendRequest(from_user_id=self.alice_id, to_user_id=self.bob_id, status='pending')
            db.session.add(request)
            db.session.commit()

            result = FriendRequest.query.filter_by(from_user_id=self.alice_id, to_user_id=self.bob_id).first()
            self.assertIsNotNone(result)
            self.assertEqual(result.status, 'pending')

    def test_accept_friend_request(self):
        with self.app.app_context():
            request = FriendRequest(from_user_id=self.alice_id, to_user_id=self.bob_id, status='pending')
            db.session.add(request)
            db.session.commit()

            request.status = 'accepted'
            db.session.commit()

            updated = FriendRequest.query.filter_by(from_user_id=self.alice_id, to_user_id=self.bob_id).first()
            self.assertEqual(updated.status, 'accepted')

    def test_cannot_add_self_as_friend_route(self):
        # Log in as Alice
        self.client.post('/signin', data={
            'username': 'alice',
            'password': 'Password123!'
        }, follow_redirects=True)

        # Attempt to add self as friend
        response = self.client.post('/add_friend', json={
            'to_username': 'alice'
        }, follow_redirects=True)

        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('You cannot add yourself', data.get('message', ''),
                    msg='Expected error when trying to add self as friend.')

        # Confirm no friend request was created
        with self.app.app_context():
            request = FriendRequest.query.filter_by(
                from_user_id=self.alice_id,
                to_user_id=self.alice_id
            ).first()
            self.assertIsNone(request, msg='Friend request to self should not exist.')
    
    def test_add_nonexistent_user(self):
        self.client.post('/signin', data={'username': 'alice', 'password': 'Password123!'}, follow_redirects=True)

        response = self.client.post('/add_friend', json={'to_username': 'charlie'}, follow_redirects=True)
        data = response.get_json()

        self.assertIn('User not found', data.get('message', ''))

    def test_reject_friend_request(self):
        with self.app.app_context():
            # Alice -> Bob
            request = FriendRequest(from_user_id=self.alice_id, to_user_id=self.bob_id, status='pending')
            db.session.add(request)
            db.session.commit()
            req_id = request.id

        # Log in as Bob
        self.client.post('/signin', data={'username': 'bob', 'password': 'Password123!'}, follow_redirects=True)

        # Bob rejects
        response = self.client.post('/respond_request', json={
            'request_id': req_id,
            'action': 'reject'
        }, follow_redirects=True)

        data = response.get_json()
        self.assertIn('Request rejected', data.get('message', ''))

        with self.app.app_context():
            updated = FriendRequest.query.get(req_id)
            self.assertEqual(updated.status, 'rejected')



                



if __name__ == '__main__':
    unittest.main()
