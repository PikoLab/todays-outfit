import unittest
from server import app
from server.routes import _check_login_auth


class TestTodaysOutfit(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_login_password(self):
        # test: correct email and password
        self.assertEqual(_check_login_auth('test2@gmail.com', 'wear')['valid'], True)

        # test: wrong password
        self.assertEqual(_check_login_auth('test2@gmail.com', 'test')['valid'], False)

        # test: non-existent email
        self.assertEqual(_check_login_auth('test199@gmail.com', 'wear')['valid'], False)


if __name__ == '__main__':
    unittest.main()
