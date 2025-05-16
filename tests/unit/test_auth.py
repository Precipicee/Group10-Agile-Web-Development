import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import date
import unittest
from Fittrack import create_app, db
from Fittrack.models import User
from werkzeug.security import generate_password_hash


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False  
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def register_user(self, username, email, password):
        return self.client.post('/signup', data={
            'username': username,
            'email': email,
            'password': password,
            'confirm': password
        }, follow_redirects=True)

    def login_user(self, username, password):
        return self.client.post('/signin', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def test_successful_registration(self):
        response = self.register_user('testuser', 'test@example.com', 'Password123!')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created and signed in.', response.data)


    def test_registration_duplicate_username(self):
        self.register_user('testuser', 'test@example.com', 'Password123!')
        self.client.get('/logout')  
        response = self.register_user('testuser', 'another@example.com', 'Password123!')
        self.assertIn(b'Username or email already exists!', response.data)

    def test_registration_duplicate_email(self):
        self.register_user('testuser', 'test@example.com', 'Password123!')
        self.client.get('/logout')  
        response = self.register_user('anotheruser', 'test@example.com', 'Password123!')
        self.assertIn(b'Username or email already exists!', response.data)


    def test_login_redirect_to_profile_if_incomplete(self):
        with self.app.app_context():
            user = User(username='newuser', email='new@example.com',
                        hashed_password=generate_password_hash('Password123!'))
            db.session.add(user)
            db.session.commit()

        response = self.login_user('newuser', 'Password123!')
        self.assertIn(b'Complete Your Profile', response.data)


    

    def test_login_redirect_to_home_if_profile_exists(self):
        with self.app.app_context():
            user = User(
                username='existinguser',
                email='exist@example.com',
                hashed_password=generate_password_hash('Password123!'),
                is_profile_complete=True,
                birthday=date(2000, 1, 1),
                gender='Other',
                height=170,
                current_weight=60.5,
                target_weight=55.0,
                target_weight_time_days=30,
                target_exercise_time_per_week=180,
                target_exercise_timeframe_days=60
            )
            db.session.add(user)
            db.session.commit()

        response = self.login_user('existinguser', 'Password123!')
        self.assertIn(b'Signed in successfully!', response.data)



    def test_login_wrong_password(self):
        with self.app.app_context():
            user = User(username='wrongpass', email='wrong@example.com',
                        hashed_password=generate_password_hash('Password123!'))
            db.session.add(user)
            db.session.commit()

        response = self.login_user('wrongpass', 'WrongPassword!')
        self.assertIn(b'Invalid username or password!', response.data)


    def test_login_unknown_user(self):
        response = self.login_user('nouser', 'nopassword')
        self.assertIn(b'Invalid username or password!', response.data)


if __name__ == '__main__':
    unittest.main()
