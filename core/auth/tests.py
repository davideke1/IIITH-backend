from rest_framework import status

def test_logout(self, client, user):
    data = {"username": user.username,
    "password": "test_password"}
    response = client.post(self.endpoint + "login/",
    data)
    assert response.status_code == status.HTTP_200_OK
    client.force_authenticate(user=user)
    data_refresh = {"refresh":
    response.data["refresh"]}
    response = client.post(self.endpoint + "logout/",
    data_refresh)
    assert response.status_code ==status.HTTP_204_NO_CONTENT
