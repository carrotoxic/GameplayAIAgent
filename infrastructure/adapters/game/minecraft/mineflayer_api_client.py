import httpx
import logging

class MineflayerAPIClient:
    def __init__(self, host: str, port: int, timeout: int = 30):
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def open(self):
        if self.client.is_closed:
            self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def start(self, data: dict) -> dict:
        await self.open()
        return await self._post("/start", data)

    async def step(self, data: dict) -> dict:
        await self.open()
        return await self._post("/step", data)

    async def stop(self) -> dict:
        await self.open()
        return await self._post("/stop")

    async def get_state(self) -> dict:
        await self.open()
        return await self._get("/state")

    async def _post(self, endpoint: str, data: dict = None) -> dict:
        try:
            response = await self.client.post(endpoint, json=data)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e.response.text}")
            return [["onError", {"onError": str(e)}]]
        except httpx.RequestError as e:
            logging.error(f"Request error occurred: {e}")
            return [["onError", {"onError": "Request Timeout" if isinstance(e, httpx.TimeoutException) else str(e)}]]

        try:
            return response.json()
        except Exception:
            logging.error(f"Failed to decode JSON from response: {response.text}")
            return [["onError", {"onError": "Invalid JSON response"}]]

    async def _get(self, endpoint: str) -> dict:
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logging.error(f"Request error occurred during GET: {e}")
            return {"error": str(e)}
        except Exception as e:
            logging.error(f"An unexpected error occurred during GET: {e}")
            return {"error": str(e)}

    async def close(self):
        await self.client.aclose()
