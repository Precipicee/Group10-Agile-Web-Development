import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datetime import date
from Fittrack import create_app, db
from Fittrack.models import User, FriendRequest, SharedReport
from werkzeug.security import generate_password_hash

class ShareReportTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
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

    def test_successful_share_report(self):
        with self.app.app_context():
            db.session.add(FriendRequest(from_user_id=self.alice_id, to_user_id=self.bob_id, status='accepted'))
            db.session.commit()

        self.client.post('/signin', data={'username': 'alice', 'password': 'Password123!'}, follow_redirects=True)

        response = self.client.post('/share_report?report_type=weight', data={
            'receiver_id': self.bob_id
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            record = SharedReport.query.filter_by(sender_id=self.alice_id, receiver_id=self.bob_id).first()
            self.assertIsNotNone(record)
            self.assertEqual(record.report_type, 'weight')

    def test_share_report_to_non_friend_should_fail(self):
        self.client.post('/signin', data={'username': 'alice', 'password': 'Password123!'}, follow_redirects=True)

        response = self.client.post('/share_report?report_type=weight', data={
            'receiver_id': self.bob_id
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            record = SharedReport.query.filter_by(sender_id=self.alice_id, receiver_id=self.bob_id).first()
            self.assertIsNone(record)

    def test_share_report_to_self_should_fail(self):
        self.client.post('/signin', data={'username': 'alice', 'password': 'Password123!'}, follow_redirects=True)

        response = self.client.post('/share_report?report_type=exercise', data={
            'receiver_id': self.alice_id
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            record = SharedReport.query.filter_by(sender_id=self.alice_id, receiver_id=self.alice_id).first()
            self.assertIsNone(record)

    def test_delete_shared_report_authorized(self):
        with self.app.app_context():
            # Alice → Bob 分享一个报告
            db.session.add(FriendRequest(from_user_id=self.alice_id, to_user_id=self.bob_id, status='accepted'))
            db.session.add(SharedReport(
                sender_id=self.alice_id,
                receiver_id=self.bob_id,
                report_type='exercise',
                record_user_id=self.alice_id
            ))
            db.session.commit()
            shared = SharedReport.query.filter_by(sender_id=self.alice_id, receiver_id=self.bob_id).first()
            report_id = shared.id

        # Bob 登录并尝试删除
        self.client.post('/signin', data={'username': 'bob', 'password': 'Password123!'}, follow_redirects=True)
        response = self.client.post(f'/delete_shared_report/{report_id}', follow_redirects=True)

        # 数据应被删除
        with self.app.app_context():
            deleted = SharedReport.query.get(report_id)
            self.assertIsNone(deleted, msg='Shared report should be deleted by authorized receiver.')

    def test_invalid_receiver_id_submission(self):
        # Alice 登录（无好友，无法提交表单成功）
        self.client.post('/signin', data={'username': 'alice', 'password': 'Password123!'}, follow_redirects=True)

        # 提交缺失 receiver_id 的表单
        response = self.client.post('/share_report?report_type=weight', data={}, follow_redirects=True)

        # 检查未插入数据库
        with self.app.app_context():
            record = SharedReport.query.filter_by(sender_id=self.alice_id).first()
            self.assertIsNone(record, msg='Invalid form submission should not create shared report.')


if __name__ == '__main__':
    unittest.main()
