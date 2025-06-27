# Mineflayer Environment Adapter

This directory contains the Mineflayer-based implementation of the `GameEnvironmentPort` for Minecraft integration.

## Overview

The `MineflayerEnvironmentAdapter` provides a clean, domain-driven interface to Minecraft using Mineflayer. It follows hexagonal architecture principles by implementing the `GameEnvironmentPort` interface.

## Features

- **Clean Architecture**: Implements the domain port interface
- **Automatic Setup**: Creates and manages the Mineflayer server automatically
- **Context Manager**: Supports Python context manager for automatic cleanup
- **Comprehensive Logging**: Built-in logging for debugging and monitoring
- **Error Handling**: Robust error handling with meaningful messages
- **Type Safety**: Full type hints for better development experience

## Prerequisites

1. **Minecraft Server**: A Minecraft server running on localhost:25565 (or configurable port)
2. **Node.js**: Required for running the Mineflayer server
3. **Python Dependencies**: Install the project dependencies including `requests`

## Installation

1. Install Python dependencies:
```bash
pip install -e .
```

2. The adapter will automatically create the necessary Node.js files when first used.

## Usage

### Basic Usage

```python
from infrastructure.adapters.game.minecraft.mineflayer_environment import MineflayerEnvironmentAdapter

# Create the adapter
env = MineflayerEnvironmentAdapter(
    minecraft_port=25565,
    mineflayer_port=3000,
    username="MyAgent"
)

# Reset the environment
event = env.reset()

# Execute an action
action_code = """
const goal = new GoalXZ(bot.player.position.x + 3, bot.player.position.z);
await bot.pathfinder.goto(goal);
"""
result = env.step(action_code)

# Clean up
env.close()
```

### Using Context Manager

```python
with MineflayerEnvironmentAdapter(username="Agent") as env:
    event = env.reset()
    result = env.step("await bot.lookAt(bot.player.position.offset(0, 5, 0))")
    # Automatic cleanup when exiting the context
```

### Integration with Agent Controller

```python
from application.agent_controller import AgentController
from infrastructure.adapters.game.minecraft.mineflayer_environment import MineflayerEnvironmentAdapter

# Create the environment
env = MineflayerEnvironmentAdapter(username="AIAgent")

# Create agent controller with environment
controller = AgentController(
    curriculum_service=curriculum_service,
    skill_service=skill_service,
    planner_service=planner_service,
    critic_service=critic_service,
    env=env  # Pass the environment
)

# Run the agent
controller.run()
```

## Configuration

The adapter supports several configuration options:

- `minecraft_port`: Port of the Minecraft server (default: 25565)
- `mineflayer_port`: Port for the Mineflayer server (default: 3000)
- `server_host`: Hostname of the Minecraft server (default: "localhost")
- `username`: Username for the bot (default: "Agent")
- `timeout`: Timeout for operations in seconds (default: 30)
- `log_level`: Logging level (default: "INFO")

## API Reference

### Methods

#### `reset(options: Optional[Dict] = None) -> Event`
Reset the environment and return the initial game state.

#### `step(action: Optional[str] = None) -> Event`
Execute an action and return the resulting game state.

#### `close() -> None`
Cleanly shutdown the environment.

### Event Model

The adapter returns `Event` objects with the following structure:

```python
@dataclass(frozen=True)
class Event:
    position: Dict[str, float]      # Player position {x, y, z}
    inventory: Dict[str, int]       # Inventory items and counts
    health: float                   # Player health
    hunger: float                   # Player hunger
    biome: str                      # Current biome
    nearby_blocks: List[str]        # Nearby block types
    nearby_entities: Dict[str, float]  # Nearby entities and distances
    time: str                       # Game time (day/night)
    other_blocks: List[str]         # Other blocks in the area
    equipment: Dict[str, str]       # Equipped items
    chests: List[str]               # Chest contents
```

## Mineflayer Actions

The adapter supports executing Mineflayer JavaScript code. Common actions include:

### Movement
```javascript
// Move to specific coordinates
const goal = new GoalXZ(x, z);
await bot.pathfinder.goto(goal);

// Move near a block
const goal = new GoalNear(x, y, z, range);
await bot.pathfinder.goto(goal);
```

### Block Interaction
```javascript
// Dig a block
const block = bot.blockAt(position);
await bot.dig(block);

// Place a block
await bot.placeBlock(block, vec3);
```

### Item Management
```javascript
// Equip an item
await bot.equip(item, destination);

// Use an item
await bot.activateItem();
```

### Looking
```javascript
// Look at a position
await bot.lookAt(position);
```

## Error Handling

The adapter provides comprehensive error handling:

- **Connection Errors**: Handles Minecraft server connection issues
- **Action Errors**: Captures and reports action execution failures
- **Server Errors**: Manages Mineflayer server lifecycle
- **Timeout Errors**: Handles operation timeouts gracefully

## Testing

Run the unit tests:

```bash
python -m pytest tests/unit/test_mineflayer_environment.py -v
```

## Troubleshooting

### Common Issues

1. **Minecraft Server Not Running**
   - Ensure a Minecraft server is running on the specified port
   - Check server logs for connection issues

2. **Node.js Not Installed**
   - Install Node.js and npm
   - Verify installation with `node --version` and `npm --version`

3. **Port Conflicts**
   - Ensure the Mineflayer port (default: 3000) is available
   - Check for other processes using the same port

4. **Dependencies Missing**
   - Run `npm install` in the mineflayer_server directory
   - Check that all Python dependencies are installed

### Debug Mode

Enable debug logging:

```python
env = MineflayerEnvironmentAdapter(log_level="DEBUG")
```

## Architecture

The adapter follows hexagonal architecture principles:

```
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              GameEnvironmentPort                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ implements
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         MineflayerEnvironmentAdapter                │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │           HTTP Client                      │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ communicates with
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                External Layer                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Mineflayer Server                        │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │           Mineflayer Bot                    │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ connects to
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Minecraft Server                            │
└─────────────────────────────────────────────────────────────┘
```

## Contributing

When contributing to this adapter:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure error handling is robust
5. Maintain backward compatibility when possible 