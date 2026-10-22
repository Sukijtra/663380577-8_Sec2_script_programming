# My API Data Fetcher CLI (Week 10)

A command-line interface (CLI) application demonstrating basic interaction with Web APIs.
This project uses the `requests` library to fetch and process JSON data from the [JSONPlaceholder](https://jsonplaceholder.typicode.com/) fake API.

**Topic:** Interacting with Web APIs: Fetching and Processing JSON Data

## Features

* **Fetch Single TODO**: Retrieve details of a specific TODO item by its ID (`/todos/{id}`).
* **Fetch All Posts**: Get a list of all fake blog posts (`/posts`), showing the first 5.
* **Fetch User TODOs**: Retrieve all TODO items for a particular user ID (`/todos?userId={id}`).
* **Error Handling**: Handles HTTP errors (e.g. 404), connection errors, timeouts, invalid JSON and invalid user input.
* **JSON Processing**: Parses responses with `response.json()` and reads fields with `.get()`.

## Core Concepts Demonstrated

* **APIs (Application Programming Interfaces)**: How applications communicate.
* **HTTP GET Requests**: `requests.get(url, timeout=10)`.
* **Response Object**: `status_code`, `ok`, `raise_for_status()`, `json()`.
* **`requests` Exceptions**: `HTTPError`, `ConnectionError`, `Timeout`, `RequestException`.
* **Dependency Management**: `pip` and `requirements.txt`.

## How to Run

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Sukijtra/663380577-8_Sec2_script_programming.git
    cd 663380577-8_Sec2_script_programming/my-api-fetcher
    ```
2. **Install dependencies:**
    ```bash
    # Create a virtual environment (optional, but recommended)
    python -m venv venv
    # Activate the virtual environment
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate

    # Install dependencies from requirements.txt
    pip install -r requirements.txt
    ```
3. **Run the application:**
    ```bash
    python main.py
    ```

### Example session

```
Enter your choice (1-4): 1
Enter TODO ID (e.g., 1, 5, 10): 1
Fetching data from: https://jsonplaceholder.typicode.com/todos/1

--- TODO Item Details ---
ID: 1
User ID: 1
Title: delectus aut autem
Completed: False
------------------------
Enter your choice (1-4): 1
Enter TODO ID (e.g., 1, 5, 10): 999999999
Fetching data from: https://jsonplaceholder.typicode.com/todos/999999999
HTTP Error: 404 Client Error: Not Found for url: https://jsonplaceholder.typicode.com/todos/999999999
Enter your choice (1-4): 3
Enter User ID (e.g., 1, 2, 3): 2
Fetching data from: https://jsonplaceholder.typicode.com/todos?userId=2

--- TODOs for User ID 2 ---
ID: 21 | Title: suscipit repellat esse quibusdam voluptatem incidunt | Status: Pending
ID: 22 | Title: distinctio vitae autem nihil ut molestias quo | Status: Completed
...
```

## Project Structure

```
my-api-fetcher/
├── src/
│   ├── __init__.py      # Makes 'src' a Python package
│   └── api_client.py    # Encapsulates API interaction logic (APIClient class)
├── main.py              # The main entry point of the application
├── .gitignore           # Specifies files/folders to ignore in Git
├── README.md            # This file!
└── requirements.txt     # Lists project dependencies (requests)
```

## Debugging in VS Code (with API Focus)

* **Set Breakpoints:** on `client = APIClient()` in `main.py` and on `response = requests.get(url, timeout=10)` in `src/api_client.py`.
* **Observe the Response:** Step over the request (F10) and expand `response` in the "Variables" pane: `status_code` (200), `ok` (True), `text` (raw JSON).
* **Simulate Errors:**
    * **Network Error:** change `BASE_URL` to `"http://nonexistent-api-domain.com"` → `ConnectionError` block.
    * **404 Not Found:** fetch TODO ID `999999999` → `HTTPError` block.

## Extension Ideas

* More endpoints (comments, albums, photos), logging, saving fetched data to CSV/JSON, query parameters (e.g. `?completed=true`), `Typer`/`Click` for CLI arguments.

## License

This project is open source. (You might add a specific license here later, e.g., MIT)
