import pytest
from fastapi import status as http_status


class TestStatusEndpoints:

    def test_list_statuses_empty(self, client):
        response = client.get("/statuses/")
        assert response.status_code == http_status.HTTP_200_OK
        assert response.json() == []

    def test_list_statuses_with_data(self, client, sample_status):
        response = client.get("/statuses/")
        assert response.status_code == http_status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_status.name

    def test_get_status_success(self, client, sample_status):
        response = client.get(f"/statuses/{sample_status.statusID}")
        assert response.status_code == http_status.HTTP_200_OK
        data = response.json()
        assert data["statusID"] == sample_status.statusID
        assert data["name"] == sample_status.name

    def test_get_status_not_found(self, client):
        response = client.get("/statuses/9999")
        assert response.status_code == http_status.HTTP_404_NOT_FOUND

    def test_create_status_success(self, client):
        payload = {
            "name": "In Progress",
            "color": "#FFA500",
            "position": 0,
        }
        response = client.post("/statuses/", json=payload)
        assert response.status_code == http_status.HTTP_201_CREATED
        data = response.json()
        assert "message" in data
        assert data["status"]["name"] == "In Progress"

    def test_create_status_duplicate_name(self, client, sample_status):
        payload = {
            "name": sample_status.name,
            "color": "#FF0000",
            "position": 1,
        }
        response = client.post("/statuses/", json=payload)
        assert response.status_code == http_status.HTTP_409_CONFLICT

    def test_update_status_success(self, client, sample_status):
        payload = {
            "name": "Updated Status",
            "color": "#00FF00",
            "position": 5,
        }
        response = client.put(f"/statuses/{sample_status.statusID}", json=payload)
        assert response.status_code == http_status.HTTP_200_OK
        data = response.json()
        assert data["status"]["name"] == "Updated Status"

    def test_update_status_not_found(self, client):
        payload = {"name": "New Name", "color": "#000000", "position": 0}
        response = client.put("/statuses/9999", json=payload)
        assert response.status_code == http_status.HTTP_404_NOT_FOUND

    def test_delete_status_success(self, client, sample_status):
        response = client.delete(f"/statuses/{sample_status.statusID}")
        assert response.status_code == http_status.HTTP_200_OK
        
        get_response = client.get(f"/statuses/{sample_status.statusID}")
        assert get_response.status_code == http_status.HTTP_404_NOT_FOUND

    def test_delete_status_not_found(self, client):
        response = client.delete("/statuses/9999")
        assert response.status_code == http_status.HTTP_404_NOT_FOUND

    def test_reorder_statuses(self, client, sample_status, sample_status_2):
        payload = [
            {"statusID": sample_status_2.statusID, "position": 0},
            {"statusID": sample_status.statusID, "position": 1},
        ]
        response = client.put("/statuses/reorder", json=payload)
        assert response.status_code == http_status.HTTP_200_OK
        data = response.json()
        assert "reordered successfully" in data["message"]

    def test_reorder_statuses_empty(self, client):
        response = client.put("/statuses/reorder", json=[])
        assert response.status_code == http_status.HTTP_400_BAD_REQUEST
