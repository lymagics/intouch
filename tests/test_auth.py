import email
import unittest
from time import sleep

from chat import create_app
from chat.models import db, User
from config import TestConfig


class AuthTestCase(unittest.TestCase):
    config = TestConfig
    
    def setUp(self):
        self.app = create_app(self.config)
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
        db.create_all()
        
    def test_password_inaccessable(self):
         u = User(username="john", password="dog", email="john@test.com")
         with self.assertRaises(AttributeError):
             u.password
             
    def test_hash_salts_are_random(self):
        u1 = User(username="bob", password="dog", email="bob@test.com")
        u2 = User(username="alice", password="cat", email="alice@test.com")
        self.assertTrue(u1.password_hash != u2.password_hash)
             
    def test_password_correct(self):
        u = User(username="sussan", password="dog", email="sussan@test.com")
        self.assertTrue(u.verify_password("dog"))
        self.assertFalse(u.verify_password("cat"))
             
    def test_auth_token_valid(self):
        u = User(username="mike", password="dog", email="mike@test.com")
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token()
        self.assertTrue(u.verify_auth_token(token))
            
    def test_auth_token_expired(self):
        u = User(username="kate", password="dog", email="kate@test.com")
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token(expiration=2)
        sleep(3)
        self.assertFalse(u.verify_auth_token(token))
             
    def test_email_token_valid(self):
        u = User(username="sam", email="sam@example.com", password="dog")
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_token(new_email="new_sam@example.com")
        self.assertTrue(u.verify_email_token(token))
             
    def test_email_token_expired(self):
        u = User(username="jake", email="jake@example.com", password="dog")
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_token(new_email="new_john@example.com", expiration=2)
        sleep(3)
        self.assertFalse(u.verify_email_token(token))
       
    def test_reset_token_valid(self):
        u = User(username="julia", password="dog", email="julia@test.com")
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.verify_reset_token(token=token, new_password="cat"))
     
    def test_reset_token_expired(self):
        u = User(username="paul", password="dog", email="paul@test.com")
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token(expiration=2)
        sleep(3)
        self.assertFalse(User.verify_reset_token(token=token, new_password="cat"))
             
    def tearDown(self):
        db.drop_all()
        self.app_ctx.pop()
             