from locust import HttpUser, task, between


class ServerPerform(HttpUser):
    wait_time = between(1, 5)
    competition_name = "Spring Festival"
    club_name = "Simply Lift"

    @task
    def load_index(self):
        self.client.get("/")

    @task
    def load_show_summary(self):
        self.client.post("/showSummary", {
            "email": "example@example.com"
        })

    @task
    def load_book_competition(self):
        self.client.get(f"/book/{self.competition_name}/{self.club_name}")

    @task
    def load_purchase_places(self):
        self.client.post("/purchasePlaces", {
            "competition": self.competition_name,
            "club": self.club_name,
            "places": 15
        })

    @task
    def load_show_points(self):
        self.client.get("/showPoints")

    @task
    def load_logout(self):
        self.client.get("/logout")
