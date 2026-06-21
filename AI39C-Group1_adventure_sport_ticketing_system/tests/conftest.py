import pytest
from flask import Flask

# A bare Flask app, used only to give render_template()/jsonify() a valid
# application context to run inside during tests. We don't load the real
# templates folder -- tests that hit render_template() patch it directly
# (see individual test files) since the actual .html templates aren't part
# of this test target.
_test_app = Flask(__name__)


@pytest.fixture(autouse=True)
def app_context():
    """Push a Flask application + request context around every test so
    that session, jsonify(), url_for(), flash(), etc. don't blow up with
    'working outside of application/request context' errors.
    """
    with _test_app.test_request_context():
        yield


@pytest.fixture
def mock_session():
    """A blank fake session dict, matching what the existing reference
    tests (tests/test_event_control.py, tests/test_auth_control.py) expect
    to receive as a fixture. The tests themselves still wrap the real
    `session` object with their own `with patch(...):` blocks for the
    actual values they need, so this fixture mostly just needs to exist.
    """
    return {}
