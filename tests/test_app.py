
import sqlite3

import pytest

from app import app, init_db


@pytest.fixture
def client(tmp_path):
    # Give each test its own temporary database.
    test_database = tmp_path / "test_feedback.db"

    app.config["TESTING"] = True
    app.config["DATABASE"] = str(test_database)

    init_db()

    with app.test_client() as client:
        yield client


def get_feedback_rows(database):
    with sqlite3.connect(database) as connection:
        return connection.execute(
            """
            SELECT name, country, email, message
            FROM feedback
            """
        ).fetchall()


def test_homepage_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Learning by building" in response.data


def test_feedback_saved_with_email(client):
    response = client.post(
        "/feedback",
        data={
            "name": "Abdi",
            "country": "Somalia",
            "email": "abdi@example.com",
            "message": "Keep learning and building projects."
        }
    )

    assert response.status_code == 200
    assert b"Your advice has been received" in response.data

    rows = get_feedback_rows(app.config["DATABASE"])

    assert len(rows) == 1
    assert rows[0] == (
        "Abdi",
        "Somalia",
        "abdi@example.com",
        "Keep learning and building projects."
    )


def test_feedback_saved_without_email(client):
    response = client.post(
        "/feedback",
        data={
            "name": "Ahmed",
            "country": "Türkiye",
            "email": "",
            "message": "Your website looks good."
        }
    )

    assert response.status_code == 200

    rows = get_feedback_rows(app.config["DATABASE"])

    assert len(rows) == 1
    assert rows[0][2] is None


def test_feedback_rejects_missing_required_fields(client):
    response = client.post(
        "/feedback",
        data={
            "name": "",
            "country": "Somalia",
            "email": "",
            "message": "Hello"
        }
    )

    assert response.status_code == 400

    rows = get_feedback_rows(app.config["DATABASE"])

    assert len(rows) == 0


def test_feedback_rejects_invalid_email(client):
    response = client.post(
        "/feedback",
        data={
            "name": "Abdi",
            "country": "Somalia",
            "email": "not-an-email",
            "message": "Hello"
        }
    )

    assert response.status_code == 400

    rows = get_feedback_rows(app.config["DATABASE"])

    assert len(rows) == 0

