# main.py
import asyncio
import uvicorn
import httpx
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from typing import Optional
import websockets
from starlette.websockets import WebSocketState
from fastapi.responses import StreamingResponse, FileResponse
from application.agent_controller import AgentController
from application.composition import build_agent
from infrastructure.websocket.agent_ws_server import manager

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- FastAPI App Initialization ---
app = FastAPI()

# For Cloud Run, you'll want to configure this securely.
# For local development, allowing all origins is fine.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# --- Agent Dependency Injection (Lazy Initialization) ---
# Will be initialized on the first request to avoid slow startup
agent_controller_instance: Optional[AgentController] = None

async def get_agent_controller() -> AgentController:
    logging.info("--- GET AGENT CONTROLLER CALLED ---")
    """
    Initializes and returns a single, shared instance of the AgentController.
    This uses a lazy initialization pattern to ensure the agent is only built
    when the first request comes in, speeding up Cloud Run startup time.
    """
    global agent_controller_instance
    if agent_controller_instance is None:
        agent_controller_instance = build_agent(game="minecraft")
    logging.info("--- GET AGENT CONTROLLER RETURNED ---")
    return agent_controller_instance

# --- API Endpoints ---
@app.post("/start")
async def start_agent_endpoint(controller: AgentController = Depends(get_agent_controller)):
    """Starts the agent's main processing loop."""
    logging.info("--- /start ENDPOINT CALLED ---")
    controller.start()
    return {"message": "Agent started successfully."}

@app.post("/reset")
async def reset_agent_endpoint(controller: AgentController = Depends(get_agent_controller)):
    url = f"{VIEWER_URL}"
    """Stops and restarts the agent to reset its state."""
    await controller.restart()
    return {"message": "Agent is resetting."}

@app.post("/stop")
async def stop_agent_endpoint(controller: AgentController = Depends(get_agent_controller)):
    """Stops the agent's main processing loop."""
    await controller.stop()
    return {"message": "Agent stopped successfully."}

# --- Reverse Proxy Endpoints ---
# These endpoints will proxy requests to the internal Mineflayer servers
# (viewer and inventory) that are not exposed publicly by Cloud Run.

VIEWER_URL = "http://localhost:3001"
INVENTORY_URL = "http://localhost:3002"
# Create a single, reusable client for all proxy requests
# This is much more efficient than creating a new client for every request.
client = httpx.AsyncClient()

@app.api_route("/viewer", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.api_route("/viewer/{path:path}")
async def proxy_viewer(request: Request, path: str = ""):
    query = request.url.query
    url = f"{VIEWER_URL}/{path}"
    if query:
        url += f"?{query}"

    logging.info(f"Streaming /viewer request for path: '{path}' to {url}")
    try:
        proxied_request = client.build_request(
            request.method, url,
            headers=request.headers,
            content=await request.body()
        )
        proxied_response = await client.send(proxied_request, stream=True)
        return StreamingResponse(
            proxied_response.aiter_raw(),
            status_code=proxied_response.status_code,
            headers=proxied_response.headers
        )
    except httpx.RequestError as exc:
        logging.error(f"Error proxying /viewer request to {url}: {exc}")
        return Response(content=f"Error connecting to viewer service: {exc}", status_code=502)

@app.api_route("/inventory", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.api_route("/inventory/{path:path}")
async def proxy_inventory(request: Request, path: str = ""):
    query = request.url.query
    url = f"{INVENTORY_URL}/{path}"
    if query:
        url += f"?{query}"

    logging.info(f"Streaming /inventory request for path: '{path}' to {url}")
    try:
        proxied_request = client.build_request(
            request.method, url,
            headers=request.headers,
            content=await request.body()
        )
        proxied_response = await client.send(proxied_request, stream=True)
        return StreamingResponse(
            proxied_response.aiter_raw(),
            status_code=proxied_response.status_code,
            headers=proxied_response.headers
        )
    except httpx.RequestError as exc:
        logging.error(f"Error proxying /inventory request to {url}: {exc}")
        return Response(content=f"Error connecting to inventory service: {exc}", status_code=502)

# --- Static Asset Proxies ---
# These routes are needed because the viewer/inventory pages request assets from absolute paths.

@app.api_route("/global.css")
async def proxy_inventory_global_css(request: Request):
    return await proxy_inventory(request, "global.css")

@app.api_route("/build/{path:path}")
async def proxy_inventory_build(request: Request, path: str):
    return await proxy_inventory(request, f"build/{path}")

@app.api_route("/index.js")
async def proxy_viewer_index_js(request: Request):
    return await proxy_viewer(request, "index.js")

@app.api_route("/socket.io/{path:path}", methods=["GET", "POST"])
async def proxy_socket_io(request: Request, path: str):
    # This single route handles the initial HTTP polling for both viewers
    # by checking the referrer header to see which page requested it.
    # The actual viewer server path is always /socket.io/
    referer = request.headers.get("referer", "")
    if "/viewer" in referer:
        logging.info(f"Proxying socket.io request from viewer: {path}")
        return await proxy_viewer(request, f"socket.io/{path}")
    elif "/inventory" in referer:
        logging.info(f"Proxying socket.io request from inventory: {path}")
        return await proxy_inventory(request, f"socket.io/{path}")
    
    # Fallback for direct requests or unknown referers
    logging.warning(f"Unknown socket.io request referer: {referer}")
    return await proxy_viewer(request, f"socket.io/{path}")


@app.api_route("/viewersocket.io/{path:path}", methods=["GET", "POST"])
async def proxy_viewer_socket_io(request: Request, path: str):
    # 上流は常に viewer の /socket.io/
    return await proxy_viewer(request, f"socket.io/{path}")

@app.websocket("/viewersocket.io/")
async def proxy_viewer_websocket_endpoint(websocket: WebSocket):
    uri = f"ws://localhost:3001/socket.io/?{websocket.url.query}"
    await proxy_viewer_websocket(websocket, uri)

# inventory 用: /inventorysocket.io/...
@app.api_route("/inventorysocket.io/{path:path}", methods=["GET", "POST"])
async def proxy_inventory_socket_io(request: Request, path: str):
    return await proxy_inventory(request, f"socket.io/{path}")

@app.websocket("/inventorysocket.io/")
async def proxy_inventory_websocket_endpoint(websocket: WebSocket):
    uri = f"ws://localhost:3002/socket.io/?{websocket.url.query}"
    # This reuses the generic proxy logic, but points to the inventory service
    await proxy_viewer_websocket(websocket, uri)

@app.websocket("/socket.io/")
async def proxy_websocket(websocket: WebSocket):
    # This single websocket proxy can handle both viewers by determining the
    # correct upstream target dynamically. For now, we assume viewer.
    # A more robust solution might inspect the path or query params if needed.
    # NOTE: The client's initial HTTP request's referer is not available here.
    # We will default to proxying to the main world viewer.
    uri = f"ws://localhost:3001/socket.io/?{websocket.url.query}"
    await proxy_viewer_websocket(websocket, uri)

# This function is now a generic helper that can be called by other proxies
async def proxy_viewer_websocket(websocket: WebSocket, uri: str):
    """
    Generic WebSocket proxy logic.
    """
    await websocket.accept()
    logging.info(f"Attempting to proxy WebSocket connection to {uri}")
    try:
        async with websockets.connect(uri) as upstream_ws:
            logging.info(f"Successfully connected to upstream WebSocket: {uri}")

            async def client_to_upstream():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await upstream_ws.send(data)
                except WebSocketDisconnect:
                    logging.info("Client disconnected from WebSocket.")
                except Exception as e:
                    logging.info(f"client_to_upstream broke: {e}")

            async def upstream_to_client():
                try:
                    while True:
                        data = await upstream_ws.recv()
                        await websocket.send_text(data)
                except websockets.exceptions.ConnectionClosed:
                    logging.info("Upstream WebSocket disconnected.")
                except Exception as e:
                    logging.info(f"upstream_to_client broke: {e}")

            client_task = asyncio.create_task(client_to_upstream())
            upstream_task = asyncio.create_task(upstream_to_client())

            done, pending = await asyncio.wait(
                [client_task, upstream_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            logging.info(f"WebSocket proxy to {uri} closed.")

    except Exception as e:
        logging.error(f"WebSocket proxy error for {uri}: {e}")
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()

@app.api_route("/worker.js")
async def proxy_viewer_worker_js(request: Request):
    return await proxy_viewer(request, "worker.js")

# for textures
@app.api_route("/textures/{file_path:path}")
async def proxy_viewer_textures(request: Request, file_path: str):
    # -> http://localhost:3001/textures/……
    return await proxy_viewer(request, f"textures/{file_path}")

# for blocksStates
@app.api_route("/blocksStates/{file_path:path}")
async def proxy_viewer_block_states(request: Request, file_path: str):
    # -> http://localhost:3001/blocksStates/……
    return await proxy_viewer(request, f"blocksStates/{file_path}")

# @app.api_route("/assets/{path:path}")
# async def proxy_viewer_general_assets(request: Request, path: str):
#     return await proxy_viewer(request, f"assets/{path}")

@app.api_route("/windows/{path:path}")
async def proxy_inventory_windows(request: Request, path: str):
    return await proxy_inventory(request, f"windows/{path}")

# --- WebSocket Endpoint ---
@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    """Handles incoming WebSocket connections."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive, listening for messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected from websocket.")

# --- Static Files and Main Entry ---
# This will be the location of our built React frontend
static_files_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.exists(static_files_path):
    app.mount("/", StaticFiles(directory=static_files_path, html=True), name="static")

# --- Main Entry Point ---
if __name__ == "__main__":
    print("Starting server...")
    # When deploying to Cloud Run, the entry point will be configured to run this.
    # e.g., using `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)