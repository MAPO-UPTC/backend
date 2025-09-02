import requests

token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImVmMjQ4ZjQyZjc0YWUwZjk0OTIwYWY5YTlhMDEzMTdlZjJkMzVmZTEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbWFwby1jNTliNiIsImF1ZCI6Im1hcG8tYzU5YjYiLCJhdXRoX3RpbWUiOjE3NTY2OTg5MDUsInVzZXJfaWQiOiIyYkZOT2NBSUExYllvUXJxZUxlNnZJWjdWa2YxIiwic3ViIjoiMmJGTk9jQUlBMWJZb1FycWVMZTZ2SVo3VmtmMSIsImlhdCI6MTc1NjY5ODkwNSwiZXhwIjoxNzU2NzAyNTA1LCJlbWFpbCI6ImRlYW0xMGh3QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJkZWFtMTBod0BnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.I-A-FT2VTfpujm3ZQLAOFxFV4D8jDCPLgcL9KaQycExTH0Tu3kc87oje8ruPwh-JR5a6dBD4YxL_H7Rpcq2cEh1-eRF4viLxMrqev2tw4qUbvA8-yMddRTrhDlp4xAXNNw0hsosqyTgUjQB0kJKmjZkO19xcEi3FKiODXrECfP3zFjDYr8iW7VOZew6uR-aHn9zLbWbwxDva-NAE6n4CjuspH9ekbeWkHRdjWrAfst5XvjUm1BvfIAjVfyoj62z3XFA1HhxQLPLkuxTEw_vLpUaVugNpr4M_NDyyQWSLby_LWYmV6oae8sOD1EqBdCO6fSeW3XBK1lTt51e2FHUjzw"

def test_validate_token():
    headers = {"Authorization": token}
    response = requests.post(
        "http://localhost:8000/ping",
        headers=headers
    )
    print(response.text)
    return response.text

# print(test_validate_token())


def test_get_users():
    response = requests.get("http://localhost:8000/users")
    print(response.request)
    return response.json()

test_get_users()