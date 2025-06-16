# 🧠 AI Gameplay Agent – Minecraft First

This project is a **modular, LLM-powered AI agent** framework designed to play and learn in sandbox-style games, starting with **Minecraft**, and extensible to other environments like **Pokémon** or **custom RPGs**.

Built using:
- 🧱 **Clean + Hexagonal Architecture**
- ⚙️ Modular Component Design
- ⚡ LLM Planning + Multi-Memory System
- 🗨️ Optional Chat-based Agent Collaboration

---

## 🚀 Features

✅ Minecraft control via [Mineflayer]  
✅ OpenAI / Mixtral / Local LLM support  
✅ Memory system: Episodic, Semantic, Procedural  
✅ Modular plugin-based game adapter  
✅ Event-driven internal communication  
✅ Clean separation of agent logic from game backend  
✅ Extensible to multi-agent communication or new games

---

## 🏛️ Architecture Summary

The architecture follows a **Hybrid MSOA + Clean Architecture** style:

```

Presentation Layer   →   Application Layer   →   Domain Core   →   Infrastructure
(CLI/WS/UI)              (AgentController)       (Planner, Memory Port)   (OpenAI, Mineflayer, FAISS)

````

Each layer is fully decoupled and testable.

🔧 **You can plug in:**
- different games (e.g., Pokémon)
- different LLMs (e.g., LLaMA, GPT-4, Claude)
- different memory systems (e.g., LangChain, Chroma)

---

## 🗂️ Project Structure

| Directory        | Purpose                                                 |
|------------------|----------------------------------------------------------|
| `agent/`         | Agent orchestration + planning logic (Clean core)       |
| `adapters/`      | Connect to real systems: LLM, Minecraft, Memory         |
| `interface/`     | CLI / WebSocket APIs                                    |
| `events/`        | Internal event bus for pub-sub system                   |
| `prompts/`       | Prompt templates for LLM generation                     |
| `configs/`       | YAML configs for different agent setups                 |
| `scripts/`       | Launchers, evaluation, utilities                        |
| `tests/`         | Unit & integration test suites                          |

---

## 📦 Requirements

- Python 3.9+
- Node.js (for Mineflayer + bridge)
- pip / Poetry
- OpenAI or Together.ai API key (optional)

---

## 🛠️ Setup

```bash
git clone https://github.com/yourname/ai-agent.git
cd ai-agent

# Install dependencies
pip install -r requirements.txt

# Optional: run Mineflayer JS bot (you'll write bridge.js)
node minecraft-bot/bridge.js

# Run the agent
python scripts/launch_agent.py
````

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 🌍 Extending to Other Games

To support new games:

1. Implement a new `GameEnvPort` adapter:

   ```python
   class PokemonAdapter(GameEnvPort):
       def observe(self): ...
       def execute_action(self, code): ...
   ```
2. Add new YAML config in `configs/`
3. Optionally define new prompt templates

No changes needed to the core agent logic.

---

## 🧠 Key Concepts

| Concept               | Description                                              |
| --------------------- | -------------------------------------------------------- |
| **Beliefs**           | Agent's internal view of the game world                  |
| **Desires**           | Goals (e.g., “mine wood”)                                |
| **Intentions**        | Concrete actions to achieve goals                        |
| **Episodic Memory**   | Stores past events, failures, successes                  |
| **Semantic Memory**   | Stores distilled facts ("dirt can be mined bare-handed") |
| **Procedural Memory** | Stores reusable code (skills)                            |

---

## 📄 License

MIT License

---

## 📬 Contact

Built with 💪 by \[Shinichi Arimura]
Twitter / GitHub / Email links here


---

## 📚 References

This project is inspired by the following works:

- **Voyager: An Open-Ended Embodied Agent with LLMs**  
  Zhou, X., et al. (2023)  
  [arXiv:2305.16291](https://arxiv.org/abs/2305.16291)

- **MindForge: A Modular Agent Architecture for Minecraft and Beyond**  
  Heng, T., et al. (2023)  
  [arXiv:2310.02296](https://arxiv.org/abs/2310.02296)

- **ReAct: Synergizing Reasoning and Acting in Language Models**  
  Yao, S., et al. (2022)  
  [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)

> If you use or extend this project, please consider citing those original works.