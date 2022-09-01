import unittest

from flask import current_app

from chat import create_app
from chat.extensions import db
from config import TestConfig


class BaseTestCase(unittest.TestCase):
    config = TestConfig
    
    def setUp(self):
        self.app = create_app(self.config)
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()
        db.create_all()
        
    def test_app_exists(self):
        self.assertTrue(current_app is not None)
        
    def tearDown(self):
        db.drop_all()
        self.app_ctx.pop()
        