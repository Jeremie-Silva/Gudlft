from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch, call
import server


class ServerTests(TestCase):
    def setUp(self):
        server.app.testing = True
        self.client = server.app.test_client()
        self.clubs = [
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
        self.competitions = [
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

    # load_data()

    def test_load_data(self):
        result = server.load_data("tests/test_data.json")
        self.assertEqual(result, self.clubs)

    # update_files()

    @patch("json.dump")
    @patch("server.open")
    def test_update_files(self, mock_open, mock_json_dump):
        server.update_files("tests/test_data.json", {})
        mock_open.assert_called_once_with("tests/test_data.json", "w")
        mock_json_dump.assert_called_once_with(
            {'tests/test_data': {}}, mock_open().__enter__()
        )

    # date_is_in_paste()

    def test_date_is_in_paste_true(self):
        tomorrow = datetime.now() - timedelta(days=1)
        self.assertTrue(server.date_is_in_paste(tomorrow.strftime(server.DATE_FORMAT)))

    def test_date_is_in_paste_false(self):
        tomorrow = datetime.now() + timedelta(days=1)
        self.assertFalse(server.date_is_in_paste(tomorrow.strftime(server.DATE_FORMAT)))

    # index()

    @patch("server.render_template")
    def test_index(self, render_template):
        render_template.return_value = "HTML"
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        render_template.assert_called_once_with("index.html")

    # show_summary()

    @patch("server.render_template")
    def test_show_summary(self, render_template):
        render_template.return_value = "HTML"
        expected_club = {"name": "test_1", "email": "test_1@test.com", "points": "24"}
        server.clubs = self.clubs
        server.competitions = self.competitions
        response = self.client.post("/showSummary", data={"email": "test_1@test.com"})
        self.assertEqual(response.status_code, 200)
        render_template.assert_called_once_with(
            "welcome.html", club=expected_club, competitions=self.competitions
        )

    @patch("server.flash")
    @patch("server.render_template")
    def test_show_summary_not_found(self, render_template, flash):
        render_template.return_value = "HTML"
        server.clubs = self.clubs
        response = self.client.post("/showSummary", data={"email": "test"})
        self.assertEqual(response.status_code, 200)
        render_template.assert_called_once_with("index.html")
        flash.assert_called_once_with("Sorry, that email wasn't found.")

    # book()

    @patch("server.flash")
    @patch("server.render_template")
    @patch("server.date_is_in_paste")
    def test_book(self, date_is_in_paste, render_template, flash):
        render_template.return_value = "HTML"
        date_is_in_paste.return_value = False
        server.clubs = self.clubs
        server.competitions = self.competitions
        response = self.client.get("/book/competition_1/test_1")
        self.assertEqual(response.status_code, 200)
        render_template.assert_called_once_with(
            "booking.html", club=self.clubs[0], competition=self.competitions[0]
        )
        flash.assert_not_called()

    @patch("server.flash")
    @patch("server.render_template")
    @patch("server.date_is_in_paste")
    def test_book_club_not_found(self, date_is_in_paste, render_template, flash):
        render_template.return_value = "HTML"
        date_is_in_paste.return_value = False
        server.clubs = self.clubs
        server.competitions = self.competitions
        response = self.client.get("/book/competition_1/test_another")
        self.assertEqual(response.status_code, 200)
        render_template.assert_called_once_with(
            "welcome.html", club="test_another", competitions=self.competitions
        )
        flash.assert_called_once_with("Something went wrong-please try again")

    @patch("server.flash")
    @patch("server.render_template")
    @patch("server.date_is_in_paste")
    def test_book_competition_not_found(self, date_is_in_paste, render_template, flash):
        render_template.return_value = "HTML"
        date_is_in_paste.return_value = False
        server.clubs = self.clubs
        server.competitions = self.competitions
        response = self.client.get("/book/competition_another/test_1")
        self.assertEqual(response.status_code, 200)
        render_template.assert_called_once_with(
            "welcome.html", club="test_1", competitions=self.competitions
        )
        flash.assert_called_once_with("Something went wrong-please try again")

    @patch("server.flash")
    @patch("server.render_template")
    @patch("server.date_is_in_paste")
    def test_book_event_is_in_paste(self, date_is_in_paste, render_template, flash):
        render_template.return_value = "HTML"
        date_is_in_paste.return_value = True
        server.clubs = self.clubs
        server.competitions = self.competitions
        response = self.client.get("/book/competition_1/test_1")
        self.assertEqual(response.status_code, 200)
        render_template.assert_called_once_with(
            "welcome.html", club=self.clubs[0], competitions=self.competitions
        )
        flash.assert_called_once_with("The event is finish")

    # purchase_places()

    @patch("server.flash")
    @patch("server.render_template")
    @patch("server.update_files")
    @patch("server.date_is_in_paste")
    def test_purchase_places(self, date_is_in_paste, update_files, render_template, flash):
        render_template.return_value = "HTML"
        date_is_in_paste.return_value = False
        server.clubs = self.clubs
        server.competitions = self.competitions
        data = {"club": "test_1", "competition": "competition_1", "places": "12"}
        response = self.client.post("/purchasePlaces", data=data)
        self.assertEqual(response.status_code, 200)
        update_files.assert_has_calls([
            call('competitions.json', [
                {'name': 'competition_1', 'date': '2025-03-27 10:00:00', 'numberOfPlaces': '13'},
                {'name': 'competition_2', 'date': '2020-10-22 13:30:00', 'numberOfPlaces': '13'}
            ]),
            call('clubs.json', [
                {'name': 'test_1', 'email': 'test_1@test.com', 'points': '12'},
                {'name': 'test_2', 'email': 'test_2@test.com', 'points': '4'},
                {'name': 'test_3', 'email': 'test_3@test.com', 'points': '13'}
            ])
        ])
        flash.assert_called_once_with("Great-booking complete!")
        expected_club = {"name": "test_1", "email": "test_1@test.com", "points": "12"}
        render_template.assert_called_once_with(
            "welcome.html", club=expected_club, competitions=self.competitions
        )

    @patch("server.flash")
    @patch("server.render_template")
    @patch("server.update_files")
    @patch("server.date_is_in_paste")
    def test_purchase_places_in_paste_reject(self, date_is_in_paste, update_files, render_template, flash):
        render_template.return_value = "HTML"
        date_is_in_paste.return_value = True
        server.clubs = self.clubs
        server.competitions = self.competitions
        data = {"club": "test_1", "competition": "competition_1", "places": "12"}
        response = self.client.post("/purchasePlaces", data=data)
        self.assertEqual(response.status_code, 200)
        update_files.assert_not_called()
        flash.assert_called_once_with("The event is finish")
        expected_club = {"name": "test_1", "email": "test_1@test.com", "points": "24"}
        render_template.assert_called_once_with(
            "welcome.html", club=expected_club, competitions=self.competitions
        )

    @patch("server.flash")
    @patch("server.render_template")
    @patch("server.update_files")
    @patch("server.date_is_in_paste")
    def test_purchase_places_insufficient_points(self, date_is_in_paste, update_files, render_template, flash):
        render_template.return_value = "HTML"
        date_is_in_paste.return_value = False
        server.clubs = self.clubs
        server.competitions = self.competitions
        data = {"club": "test_2", "competition": "competition_1", "places": "5"}
        response = self.client.post("/purchasePlaces", data=data)
        self.assertEqual(response.status_code, 200)
        update_files.assert_not_called()
        flash.assert_called_once_with("You cannot book more places than the points you have.")
        expected_club = {"name": "test_2", "email": "test_2@test.com", "points": "4"}
        render_template.assert_called_once_with(
            "welcome.html", club=expected_club, competitions=self.competitions
        )

    @patch("server.flash")
    @patch("server.render_template")
    @patch("server.update_files")
    @patch("server.date_is_in_paste")
    def test_purchase_places_exceeds_limit(self, date_is_in_paste, update_files, render_template, flash):
        render_template.return_value = "HTML"
        date_is_in_paste.return_value = False
        server.clubs = self.clubs
        server.competitions = self.competitions
        data = {"club": "test_1", "competition": "competition_1", "places": "13"}
        response = self.client.post("/purchasePlaces", data=data)
        self.assertEqual(response.status_code, 200)
        update_files.assert_not_called()
        flash.assert_called_once_with("You cannot book more places than 12.")
        expected_club = {"name": "test_1", "email": "test_1@test.com", "points": "24"}
        render_template.assert_called_once_with(
            "welcome.html", club=expected_club, competitions=self.competitions
        )

    # logout()

    @patch("server.redirect")
    @patch("server.url_for")
    def test_logout(self, url_for, redirect):
        redirect.return_value = "HTML"
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 200)
        url_for.assert_called_once_with("index")
        redirect.assert_called_once_with(url_for())

    # show_points()

    @patch("server.render_template")
    def test_show_points(self, render_template):
        render_template.return_value = "HTML"
        server.clubs = self.clubs
        response = self.client.get("/showPoints")
        self.assertEqual(response.status_code, 200)
        render_template.assert_called_once_with(
            "show_points.html", clubs=self.clubs
        )
