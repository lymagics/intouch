import unittest

from chat import create_app
from chat.models import db, User, Room, Category, Message
from config import TestConfig


class UtilsTestCase(unittest.TestCase):
    config = TestConfig
    
    def setUp(self):
        self.app = create_app(self.config)
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
        db.create_all()
        
    def test_gravatar_url_parameters(self):
        u = User(username="bob", email="bob@test.com", password="dog")
        gravatar_url = u.gravatar_url()
        email_hash = "ebf3a1ca1e3ca553e2bd873b3cd96390"
        self.assertTrue(email_hash in gravatar_url)
        self.assertTrue("s=" in gravatar_url)
        self.assertTrue("d=" in gravatar_url)
        self.assertTrue("r=" in gravatar_url)
        
    def test_room_clean(self):
        u = User(username="bob", email="bob@test.com")
        c = Category(name="Python")
        db.session.add(u)
        db.session.add(c)
        db.session.commit()
        
        r = Room(name="Let's learn Flask!", creator=u, category=c)
        db.session.add(r)
        db.session.commit()
        
        first_message = Message(sender=u, room=r)
        db.session.add(first_message)
        db.session.commit()
        
        first_message_id = first_message.message_id
        
        for i in range(20):
            m = Message(sender=u, room=r)
            db.session.add(m)
            r.clean()
            db.session.commit()
            
        first_message = Message.query.get(first_message_id)
        self.assertTrue(first_message is None)
            
    def test_room_search(self):
        u = User(username="alice", email="alice@test.com")
        c = Category(name="Flask")
        db.session.add(u)
        db.session.add(c)
        db.session.commit()
        
        r = Room(name="Let's learn Flask!", creator=u, category=c)
        db.session.add(r)
        db.session.commit()
        
        self.assertTrue(Room.search("Flask").all() is not None)
        self.assertFalse(Room.search("minecraft").all())
            
    def tearDown(self):
        db.drop_all()
        self.app_ctx.pop()
        