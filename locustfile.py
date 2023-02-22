from locust import HttpUser, task


class LocustTestUser(HttpUser):
    @task
    def upstream_order(self):
        self.client.post("/api/v1/orders/upstream/", json={})
