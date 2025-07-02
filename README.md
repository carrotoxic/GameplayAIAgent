# GameplayAI Agent

A modular AI agent framework for autonomous gameplay in Minecraft, built with FastAPI, React, and mineflayer. The agent uses large language models for planning and decision-making while maintaining episodic, semantic, and procedural memory systems.

## Architecture Overview

The project follows a clean hexagonal architecture with clear separation of concerns:

- **Domain Layer**: Core agent logic, memory systems, and business rules
- **Application Layer**: Agent controller, composition, and event handling  
- **Infrastructure Layer**: Adapters for LLMs, Minecraft, databases, and external services
- **Presentation Layer**: React frontend and WebSocket APIs

## Key Components

### Agent System
- **Planner**: Generates executable code using LLM reasoning
- **Critic**: Evaluates action outcomes and provides feedback
- **Curriculum**: Manages task progression and difficulty scaling
- **Memory System**: Maintains episodic events, semantic knowledge, and procedural skills

### Minecraft Integration
- **Mineflayer Bot**: Handles Minecraft server interaction
- **World Viewer**: Real-time 3D visualization of the bot's perspective
- **Inventory Manager**: Visual interface for bot's inventory state
- **Primitive Skills**: Reusable code modules for common actions

### Infrastructure
- **LLM Adapters**: Support for OpenAI, Google Gemini, and Ollama
- **Database**: ChromaDB for vector storage and retrieval
- **WebSocket**: Real-time communication between components

## Project Structure

```
GameplayAIAgent/
├── main.py                     # FastAPI application entry point
├── application/                # Application orchestration
│   ├── agent_controller.py     # Main agent control loop
│   ├── composition.py          # Dependency injection
│   └── event_bus.py           # Event handling system
├── domain/                     # Core business logic
│   ├── models/                # Domain models and entities
│   ├── services/              # Core agent services
│   │   ├── planner.py         # Code generation and planning
│   │   ├── critic.py          # Action evaluation
│   │   ├── curriculum.py      # Task management
│   │   └── memory.py          # Memory systems
│   ├── ports/                 # Interface definitions
│   └── events/                # Domain events
├── infrastructure/            # External integrations
│   ├── adapters/              # Implementation of ports
│   │   ├── llm/              # LLM provider adapters
│   │   ├── database/         # ChromaDB adapter
│   │   ├── game/             # Minecraft integration
│   │   └── executor/         # Code execution
│   ├── prompts/              # LLM prompt templates
│   ├── primitive_skill/      # Reusable skill definitions
│   └── websocket/            # WebSocket server
├── frontend/                  # React user interface
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   └── services/         # API communication
│   └── dist/                 # Built frontend assets
├── configs/                   # Configuration files
└── tests/                    # Test suites
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (recommended)
- Java 21 (for Minecraft server)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GameplayAIAgent
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Run with Docker (Recommended)**
   ```bash
   # Build the image
   docker build -t gameplay-ai-agent .
   
   # Run with high memory allocation
   docker run -d \
     --name gameplay-ai-agent \
     --memory=16g \
     --cpus=4 \
     -p 8000:8000 \
     -p 3001:3001 \
     -p 3002:3002 \
     -e NODE_OPTIONS=--max-old-space-size=8192 \
     --env-file .env \
     gameplay-ai-agent
   ```

4. **Alternative: Local Development**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Node.js dependencies
   cd infrastructure/adapters/game/minecraft/mineflayer_server
   npm install
   cd ../../../../frontend
   npm install && npm run build
   
   # Run the application
   python main.py
   ```

### Access Points

Once running, access the application at:

- **Main Interface**: http://localhost:8000
- **World Viewer**: http://localhost:8000/viewer
- **Inventory Panel**: http://localhost:8000/inventory
- **API Documentation**: http://localhost:8000/docs

## Configuration

### LLM Providers

Configure your preferred LLM provider in `configs/llm_config.yaml`:

```yaml
llm:
  provider: "openai"  # or "gemini", "ollama"
  model: "gpt-4"
  api_key: "${OPENAI_API_KEY}"
```

### Agent Behavior

Modify agent parameters in `configs/minecraft_config.yaml`:

```yaml
agent:
  max_iterations: 50
  memory_retrieval_count: 5
  warm_up_episodes: 3
```

## Features

### Autonomous Gameplay
- Automatic task decomposition and execution
- Dynamic code generation for complex behaviors
- Adaptive learning from successes and failures

### Memory Systems
- **Episodic**: Stores specific experiences and outcomes
- **Semantic**: Maintains factual knowledge about the game world
- **Procedural**: Develops and refines reusable skills

### Real-time Monitoring
- Live world view from the bot's perspective
- Inventory state visualization
- Planning and execution logs
- WebSocket-based real-time updates

### Extensibility
- Modular architecture supports new games and environments
- Plugin system for custom skills and behaviors
- Configurable LLM providers and memory backends

## Development

### Running Tests
```bash
pytest tests/
```

### Building Frontend
```bash
cd frontend
npm run build
```

### API Development
The FastAPI application provides REST endpoints and WebSocket connections for:
- Agent control (start/stop/reset)
- Real-time state monitoring
- Configuration management

## Deployment

### Docker Production Build
```bash
docker build -t gameplay-ai-agent:latest .
docker run -d \
  --name gameplay-ai-agent-prod \
  --memory=16g \
  --cpus=4 \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  gameplay-ai-agent:latest
```

### Google Cloud Run
The application is configured for Cloud Run deployment with proper health checks and resource limits.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

This project builds upon research in autonomous agents and reinforcement learning:

- Voyager: An Open-Ended Embodied Agent with Large Language Models
- ReAct: Synergizing Reasoning and Acting in Language Models