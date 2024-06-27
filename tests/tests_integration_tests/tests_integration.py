import pytest
from unittest import mock
import server


server.clubs = [
    {
        "name": "test_1",
        "email": "test_1@test.com",
        "points": "24"
    },
    {
        "name": "test_2",
        "email": "test_2@test.com",
        "points": "4"
    },
    {
        "name": "test_3",
        "email": "test_3@test.com",
        "points": "13"
    }
]
server.competitions = [
    {
        "name": "competition_1",
        "date": "2025-03-27 10:00:00",
        "numberOfPlaces": "25"
    },
    {
        "name": "competition_2",
        "date": "2020-10-22 13:30:00",
        "numberOfPlaces": "13"
    }
]


@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def mock_update_files():
    with mock.patch("server.update_files") as mocked_update_files:
        yield mocked_update_files


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal" in response.data


def test_show_summary_valid_email(client):
    email = "test_1@test.com"
    response = client.post("/showSummary", data={"email": email})
    assert response.status_code == 200
    assert b"Welcome, test_1@test.com" in response.data


def test_show_summary_invalid_email(client):
    email = "nonexistent@test.com"
    response = client.post("/showSummary", data={"email": email})
    assert response.status_code == 200
    assert b"Sorry, that email wasn&#39;t found." in response.data


def test_book_valid(client):
    competition = "competition_1"
    club = "test_1"
    response = client.get(f"/book/{competition}/{club}")
    assert response.status_code == 200
    assert b"Places available: 25" in response.data


def test_book_invalid_competition(client):
    competition = "nonexistent_competition"
    club = "test_1"
    response = client.get(f"/book/{competition}/{club}")
    assert response.status_code == 200
    assert b"Something went wrong-please try again" in response.data


def test_book_invalid_club(client):
    competition = "competition_1"
    club = "nonexistent_club"
    response = client.get(f"/book/{competition}/{club}")
    assert response.status_code == 200
    assert b"Something went wrong-please try again" in response.data


def test_book_event_in_past(client):
    competition = "competition_2"
    club = "test_1"
    response = client.get(f"/book/{competition}/{club}")
    assert response.status_code == 200
    assert b"The event is finish" in response.data


def test_show_points(client):
    response = client.get("/showPoints")
    assert response.status_code == 200
    assert b" test_1<br />\n            Points: 24" in response.data


def test_purchase_places_valid(client):
    data = {"club": "test_1", "competition": "competition_1", "places": "11"}
    response = client.post("/purchasePlaces", data=data)
    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data


def test_purchase_places_event_in_past(client):
    data = {"club": "test_1", "competition": "competition_2", "places": "11"}
    response = client.post("/purchasePlaces", data=data)
    assert response.status_code == 200
    assert b"The event is finish" in response.data


def test_purchase_places_insufficient_points(client):
    data = {"club": "test_2", "competition": "competition_1", "places": "5"}
    response = client.post("/purchasePlaces", data=data)
    assert response.status_code == 200
    assert b"You cannot book more places than the points you have." in response.data


def test_purchase_places_exceeds_limit(client):
    data = {"club": "test_1", "competition": "competition_1", "places": "13"}
    response = client.post("/purchasePlaces", data=data)
    assert response.status_code == 200
    assert b"You cannot book more places than 12." in response.data


def test_logout(client):
    response = client.get("/logout")
    assert response.status_code == 302
    assert response.headers['Location'] == "http://localhost/"
