# GameplayAI Agent Frontend

React-based user interface for monitoring and controlling the AI agent's gameplay in Minecraft.

## Overview

The frontend provides real-time visualization and control of the AI agent through:

- **Agent Planning Panel**: Shows current goals, planning status, and execution progress
- **World Viewer**: Embedded 3D view of the bot's perspective using Prismarine viewer
- **Inventory Panel**: Real-time display of the bot's inventory state
- **Relevant Skills**: Shows skills being considered or executed
- **WebSocket Integration**: Live updates from the agent backend

## Technology Stack

- **React 18**: UI framework with functional components and hooks
- **Vite**: Fast development server and build tool
- **Tailwind CSS**: Utility-first styling
- **WebSocket**: Real-time communication with the backend
- **Socket.IO**: Fallback for viewer integration

## Components

### Core Components
- `App.jsx`: Main application layout and routing
- `AgentPlanning.jsx`: Displays agent's current planning state and progress
- `WorldView.jsx`: Embeds the Prismarine 3D world viewer
- `InventoryPanel.jsx`: Shows bot's inventory with item icons
- `Card.jsx`: Reusable card component for consistent UI

### Hooks
- `useAgentSocket.js`: WebSocket connection management and state synchronization

### Services
- `api.js`: HTTP client for REST API communication

## Development

### Setup
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```
Starts the Vite development server with hot module replacement at http://localhost:5173

### Build for Production
```bash
npm run build
```
Generates optimized static files in the `dist/` directory

### Preview Production Build
```bash
npm run preview
```

## Integration

The frontend integrates with multiple backend services:

1. **FastAPI Backend** (port 8000): Main application API and WebSocket endpoint
2. **Prismarine Viewer** (port 3001): 3D world visualization
3. **Inventory Viewer** (port 3002): Inventory state display

### WebSocket Communication

The frontend maintains a WebSocket connection to `/ws/agent` for real-time updates:

```javascript
// Automatic protocol detection (ws:// for HTTP, wss:// for HTTPS)
const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const wsUrl = `${protocol}://${window.location.host}/ws/agent`;
```

### Data Flow

1. Agent broadcasts state changes via WebSocket
2. Frontend receives updates and re-renders components
3. User interactions trigger API calls to control agent behavior
4. Embedded viewers update independently via their own connections

## Styling

The project uses Tailwind CSS for responsive design with a dark theme optimized for monitoring dashboards. Key design principles:

- **Grid Layout**: Responsive grid adapts to different screen sizes
- **Real-time Indicators**: Visual feedback for connection status and agent state
- **Embedded Viewers**: Seamless integration of 3D world and inventory views
- **Status Colors**: Consistent color scheme for different states (success, error, pending)

## Configuration

Frontend configuration is handled through environment variables and build-time settings:

- **API Base URL**: Automatically detected from window.location
- **WebSocket URL**: Protocol-aware connection setup
- **Build Output**: Configured for Docker container deployment
