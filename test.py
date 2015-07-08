from application import app
import unittest

app.config['TESTING'] = True

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client(self)

    def tearDown(self):
        pass

    # ensure that flask was set up correctly
    def test_index(self):
        response = self.app.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def login(self, username, password):
        return self.app.post('/login',
                             data=dict(username=username, password=password),
                             follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    # test the login / logout functionality
    def test_login_logout(self):
        # successful login
        rv = self.login('admin', 'admin')
        assert 'You are now logged in' in rv.data
        # successful logout
        rv = self.logout()
        assert 'You are now logged out' in rv.data
        # wrong credential
        rv = self.login('admin', 'wrong password')
        assert 'invalid credential, please try again' in rv.data
        # invalid logout
        rv = self.logout()
        assert 'You need to log in first' in rv.data


if __name__ == '__main__':
    unittest.main()
