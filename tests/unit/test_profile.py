import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datetime import date
from Fittrack import create_app, db
from Fittrack.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from Fittrack.config import TestConfig


class ProfileTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig) 
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            user = User(
                username='profileuser',
                email='profile@example.com',
                hashed_password=generate_password_hash('Password123!'),
                is_profile_complete=False
            )
            db.session.add(user)
            db.session.commit()
            self.user_id = user.user_id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        return self.client.post('/signin', data={
            'username': 'profileuser',
            'password': 'Password123!'
        }, follow_redirects=True)

    def test_basicinfo_successful_submission(self):
        self.login()
        response = self.client.post('/basicinfo', data={
            'avatar': 'default.png',
            'birthday': '2000-01-01',
            'gender': 'Male',
            'height': 170,
            'current_weight': 65.0,
            'target_weight': 60.0,
            'target_weight_time_days': 30,
            'target_exercise_time_per_week': 120,
            'target_exercise_timeframe_days': 60
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile created successfully!', response.data)

        with self.app.app_context():
            user = User.query.get(self.user_id)
            self.assertTrue(user.is_profile_complete)
            self.assertEqual(user.height, 170)
            self.assertEqual(user.target_weight, 60.0)

    def test_basicinfo_missing_fields_should_fail(self):
        self.login()
        response = self.client.post('/basicinfo', data={
            'avatar': '',  
            'birthday': '',
            'gender': 'Male',
            'height': '',
            'current_weight': '',
            'target_weight': ''
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All required fields must be filled out correctly.', response.data)

    
    def test_change_password_wrong_current_password(self):
        self.login()
        self.client.post('/change_password', data={
            'current_password': 'WrongPassword!',
            'new_password': 'NewPass456!',
            'confirm_new_password': 'NewPass456!'
        }, follow_redirects=True)

        with self.app.app_context():
            user = db.session.get(User, self.user_id)
            
            self.assertTrue(check_password_hash(user.hashed_password, 'Password123!'))



if __name__ == '__main__':
    unittest.main()
