# my-api-fetcher/src/api_client.py
import requests  # Import the requests library


class APIClient:
    """
    A client to interact with the JSONPlaceholder API.
    """
    BASE_URL = "https://jsonplaceholder.typicode.com"

    def _make_request(self, endpoint):
        """
        Internal helper to make a GET request to a given endpoint.
        Handles common errors.
        """
        url = f"{self.BASE_URL}{endpoint}"
        print(f"Fetching data from: {url}")
        response = None
        try:
            response = requests.get(url, timeout=10)  # Added timeout for robustness
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            return response.json()  # Returns parsed JSON data
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
        except requests.exceptions.JSONDecodeError:
            # Checked before RequestException because it is a subclass of it
            print(f"Error: Could not decode JSON from response: {response.text[:100]}...")  # Show first 100 chars
        except requests.exceptions.RequestException as err:
            print(f"An unexpected error occurred: {err}")
        return None

    def fetch_single_todo(self, todo_id):
        """Fetches a single TODO item by its ID."""
        return self._make_request(f"/todos/{todo_id}")

    def fetch_all_posts(self):
        """Fetches a list of all posts."""
        return self._make_request("/posts")

    def fetch_user_todos(self, user_id):
        """Fetches all TODOs for a specific user ID."""
        return self._make_request(f"/todos?userId={user_id}")

    # You could add more methods here, e.g., fetch_comments, fetch_albums, etc.
