# from abc import ABC, abstractmethod
# from typing import Optional
# from domain.models import Event
# from domain.ports import GameEnvironmentPort

# import os
# import time
# import requests
# import json
# import warnings



# class MinecraftEnvironmentAdapter(GameEnvironmentPort):
#     def __init__(
#         self,
#         mc_port: Optional[int] = None,
#         azure_login: Optional[dict] = None,
#         server_host: str = "http://127.0.0.1",
#         server_port: int = 3000,
#         request_timeout: int = 600,
#         log_path: str = "./logs",
#     ):
#         if not mc_port and not azure_login:
#             raise ValueError("Either mc_port or azure_login must be specified")

#         if mc_port and azure_login:
#             warnings.warn("Both mc_port and azure_login specified. Using azure_login.")

#         self.mc_port = mc_port
#         self.azure_login = azure_login
#         self.server = f"{server_host}:{server_port}"
#         self.request_timeout = request_timeout
#         self.log_path = log_path
#         self.has_reset = False
#         self.reset_options = {}
#         self.server_paused = False

#         self.mineflayer = self._init_mineflayer(server_port)
#         self.mc_instance = self._init_mc_instance() if azure_login else None
#         self.connected = False

#     def _init_mineflayer(self, server_port: int) -> SubprocessMonitor:
#         U.f_mkdir(self.log_path, "mineflayer")
#         script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "mineflayer/index.js"))
#         return SubprocessMonitor(
#             commands=["node", script_path, str(server_port)],
#             name="mineflayer",
#             ready_match=r"Server started on port (\d+)",
#             log_path=U.f_join(self.log_path, "mineflayer"),
#         )

#     def _init_mc_instance(self) -> MinecraftInstance:
#         U.f_mkdir(self.log_path, "minecraft")
#         return MinecraftInstance(
#             **self.azure_login,
#             mineflayer=self.mineflayer,
#             log_path=U.f_join(self.log_path, "minecraft"),
#         )

#     def _check_and_start_process(self):
#         if self.mc_instance and not self.mc_instance.is_running:
#             print("Starting Minecraft server...")
#             self.mc_instance.run()
#             self.mc_port = self.mc_instance.port
#             self.reset_options["port"] = self.mc_port

#         if not self.mineflayer.is_running:
#             self.mineflayer.run()

#         response = requests.post(
#             f"{self.server}/start", json=self.reset_options, timeout=self.request_timeout
#         )
#         if response.status_code != 200:
#             raise RuntimeError(f"Server failed to start: {response.status_code}")
#         return response.json()

#     def reset(self, options: dict = None) -> Event:
#         options = options or {}

#         self.reset_options = {
#             "port": self.mc_port,
#             "reset": options.get("mode", "hard"),
#             "inventory": options.get("inventory", {}),
#             "equipment": options.get("equipment", []),
#             "spread": options.get("spread", False),
#             "waitTicks": options.get("wait_ticks", 5),
#             "position": options.get("position", None),
#         }

#         self._unpause()
#         self.mineflayer.stop()
#         time.sleep(1)

#         result = self._check_and_start_process()
#         self.has_reset = True
#         self.connected = True
#         self.reset_options["reset"] = "soft"
#         self._pause()
#         return Event.from_dict(json.loads(result))

#     def step(self, action: str = "", programs: str = "") -> Event:
#         if not self.has_reset:
#             raise RuntimeError("Environment must be reset before stepping.")

#         self._unpause()
#         payload = {"code": action, "helper functions": programs}
#         response = requests.post(f"{self.server}/step", json=payload, timeout=self.request_timeout)
#         self._pause()

#         if response.status_code != 200:
#             raise RuntimeError(f"Failed step: {response.status_code}")
#         return Event.from_dict(json.loads(response.json()))

#     def close(self) -> None:
#         self._unpause()
#         if self.connected:
#             requests.post(f"{self.server}/stop")
#             self.connected = False
#         if self.mc_instance:
#             self.mc_instance.stop()
#         self.mineflayer.stop()

#     def _pause(self):
#         if self.mineflayer.is_running and not self.server_paused:
#             requests.post(f"{self.server}/pause")
#             self.server_paused = True

#     def _unpause(self):
#         if self.mineflayer.is_running and self.server_paused:
#             requests.post(f"{self.server}/pause")
#             self.server_paused = False

