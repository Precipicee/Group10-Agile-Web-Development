import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import date, datetime, timedelta
from unittest.mock import patch
import unittest
from Fittrack import create_app, db
from Fittrack.models import User, DailyRecord
from werkzeug.security import generate_password_hash
import logging
logging.basicConfig(level=logging.WARNING)




class DailyRecordTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            
            user = User(
                username='dailyuser',
                email='daily@example.com',
                hashed_password=generate_password_hash('Password123!'),
                is_profile_complete=True,
                birthday=date(2000, 1, 1),
                age=24,
                gender='Other',
                height=170,
                current_weight=60.5,
                target_weight=55.0,
                target_weight_time_days=30,
                target_exercise_time_per_week=180,
                target_exercise_timeframe_days=60,
                avatar='a.png'
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
            'username': 'dailyuser',
            'password': 'Password123!'
        }, follow_redirects=True)

    def test_upload_creates_record(self):
        self.login()

        from datetime import datetime, timedelta
        valid_date = (datetime.today().date() - timedelta(days=5)).strftime('%Y-%m-%d')


        response = self.client.post('/add_record', data={
            'date': valid_date,
            'weight': 60,
            'breakfast': 'banana',
            'lunch': 'apple',
            'dinner': 'chicken',
            'exercise[]': ['running'],
            'duration[]': ['30'],
            'intensity[]': ['moderate']
        }, follow_redirects=True)

        


        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            record = DailyRecord.query.filter_by(user_id=self.user_id).first()
            self.assertIsNotNone(record, "Record should be created in DB")
            self.assertEqual(record.lunch, 'apple')
            self.assertIsNotNone(record.total_calories)
            self.assertGreater(record.total_calories, 0)
    
    def submit_record(self, date_str):
        return self.client.post('/add_record', data={
            'date': date_str,
            'weight': 60,
            'breakfast': 'banana',
            'lunch': 'apple',
            'dinner': 'chicken',
            'exercise[]': ['running'],
            'duration[]': ['30'],
            'intensity[]': ['moderate']
        }, follow_redirects=True)

    @patch('Fittrack.routes.upload_routes.estimate_calories_from_meal', return_value=1800)
    @patch('Fittrack.routes.upload_routes.estimate_calories_from_exercise', return_value=300)
    def test_gpt_called_on_upload(self, mock_exercise, mock_meal):
        self.login()

        with self.client.session_transaction() as sess:
            sess.pop('pending_record', None)

        date_str = (datetime.today().date() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.submit_record(date_str)

        mock_meal.assert_called()
        mock_exercise.assert_called()


    def test_missing_fields_error(self):
        self.login()
        date_str = (datetime.today().date() - timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post('/add_record', data={
            'date': date_str,
            'breakfast': 'banana'
        }, follow_redirects=True)
        self.assertIn(b'Error', response.data)

    def test_duplicate_record_overwrites(self):
        self.login()
        date_str = (datetime.today().date() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.submit_record(date_str)
        # Submit again with different data
        response = self.client.post('/add_record', data={
            'date': date_str,
            'weight': 62,
            'breakfast': 'toast',
            'lunch': 'rice',
            'dinner': 'fish',
            'exercise[]': ['cycling'],
            'duration[]': ['20'],
            'intensity[]': ['light']
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            record = DailyRecord.query.filter_by(user_id=self.user_id, date=datetime.strptime(date_str, '%Y-%m-%d').date()).first()
            self.assertEqual(record.breakfast, 'toast')

    def test_record_not_created_if_invalid_date(self):
        self.login()
        old_date = (datetime.today().date() - timedelta(days=200)).strftime('%Y-%m-%d')
        response = self.submit_record(old_date)
        self.assertIn(b'date is too old', response.data.lower())

    def test_flash_message_on_success(self):
        self.login()
        date_str = (datetime.today().date() - timedelta(days=2)).strftime('%Y-%m-%d')
        response = self.submit_record(date_str)
        self.assertIn(b'Record saved successfully', response.data)



if __name__ == '__main__':
    unittest.main()
