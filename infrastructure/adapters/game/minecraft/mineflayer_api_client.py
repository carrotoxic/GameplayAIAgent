import requests

class MineflayerAPIClient:
    def __init__(self, host: str, port: int, timeout: int = 30):
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout

    def start(self, data: dict) -> dict:
        return self._post("/start", data)

    def step(self, data: dict) -> dict:
        return self._post("/step", data)

    def stop(self) -> dict:
        return self._post("/stop")

    def get_state(self) -> dict:
        return self._get("/state")

    def _post(self, endpoint: str, data: dict = None) -> dict:
        try:
            response = requests.post(self.base_url + endpoint, json=data, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Non-fatal HTTP error: {e}")
            return {"error": str(e), "status_code": response.status_code}
        except requests.exceptions.ReadTimeout:
            print("⚠️ Timeout: Step request took too long.")
            return {"error": "Timeout", "status_code": 504}

        if response.status_code != 200:
            try:
                raise RuntimeError(f"Server error: {response.json().get('error')}")
            except Exception:
                response.raise_for_status()
        return response.json()

    def _get(self, endpoint: str) -> dict:
        response = requests.get(self.base_url + endpoint, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
