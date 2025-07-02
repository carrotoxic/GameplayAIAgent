import React, { useState, useEffect } from 'react';
import WorldView from './components/WorldView';
import InventoryPanel from './components/InventoryPanel';
import TaskInfo from './components/TaskInfo';
import AgentPlanning from './components/AgentPlanning';
import RelevantSkillSet from './components/RelevantSkillSet';
import { startAgent, resetAgent, stopAgent } from './services/api';
import { useAgentSocket } from './hooks/useAgentSocket';
import Card from './components/Card';

function App() {
  const { lastMessage, isConnected } = useAgentSocket();
  const [agentStarted, setAgentStarted] = useState(false);
  const [isAgentStarting, setIsAgentStarting] = useState(false);
  const [isAgentResetting, setIsAgentResetting] = useState(false);

  const [task, setTask] = useState("Press 'Start' to begin...");
  const [reasoning, setReasoning] = useState("");
  const [plan, setPlan] = useState("");
  const [thought, setThought] = useState("");
  const [code, setCode] = useState("");
  const [relevantSkills, setRelevantSkills] = useState([]);

  useEffect(() => {
    if (lastMessage) {
      console.log('Received data:', lastMessage);
      setTask(lastMessage.task?.command || "");
      setReasoning(lastMessage.task?.reasoning || "");
      setPlan(lastMessage.plan?.plan || "");
      setThought(lastMessage.plan?.thought || "");
      setCode(lastMessage.plan?.code || "");
      setRelevantSkills(lastMessage.skills || []);
    }
  }, [lastMessage]);

  const handleStart = async () => {
    setIsAgentStarting(true);
    try {
      await startAgent();
      setAgentStarted(true);
    } catch (error) {
      console.error("Error starting agent.");
    } finally {
      setIsAgentStarting(false);
    }
  };

  const handleReset = async () => {
    setIsAgentResetting(true);
    try {
      await resetAgent();
      setAgentStarted(false);
    } catch (error) {
      console.error("Error resetting agent.");
    } finally {
      setIsAgentResetting(false);
    }
  };

  const handleStop = async () => {
    try {
      await stopAgent();
    } catch (error) {
      console.error("Error stopping agent.");
    }
  };

  const LoadingPlaceholder = ({ title }) => (
    <Card className="flex-grow h-full flex items-center justify-center">
      <div className="text-center text-gray-500">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p>Waiting for agent to start...</p>
      </div>
    </Card>
  );

  return (
    <div className="min-h-screen flex flex-col p-6 bg-background text-on-background">
        <header className="flex justify-between items-center mb-6">
            <h1 className="text-4xl font-bold text-primary tracking-wider font-sans">Game Play Agent</h1>
            <div className="flex items-center gap-4">
              <span className={`text-sm ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
                {isConnected ? '● Connected' : '● Disconnected'}
              </span>
              <button
                onClick={handleStart}
                disabled={isAgentStarting || isAgentResetting}
                className="bg-primary text-on-primary font-bold py-2 px-6 rounded-lg shadow-lg hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAgentStarting ? 'Starting...' : 'Start'}
              </button>
              <button
                onClick={handleReset}
                disabled={isAgentResetting || isAgentStarting}
                className="bg-secondary text-on-primary font-bold py-2 px-6 rounded-lg shadow-lg hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAgentResetting ? 'Resetting...' : 'Reset'}
              </button>
              <button
                onClick={handleStop}
                disabled={isAgentResetting || isAgentStarting}
                className="bg-red-600 text-white font-bold py-2 px-6 rounded-lg shadow-lg hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Stop
              </button>
            </div>
        </header>
        <main className="flex-grow grid lg:grid-cols-2 gap-8 mt-4">
            {/* Left Column */}
            <div className="flex flex-col gap-8 h-full">
                <div className="flex-[3]">
                    {agentStarted ? <WorldView isStarted={agentStarted} /> : <LoadingPlaceholder title="World View" />}
                </div>
                <div className="flex-[2] grid grid-cols-5 gap-8">
                    <div className="col-span-2">
                         {agentStarted ? <InventoryPanel isStarted={agentStarted} /> : <LoadingPlaceholder title="Inventory" />}
                    </div>
                    <div className="col-span-3">
                        <RelevantSkillSet skills={relevantSkills} />
                    </div>
                </div>
            </div>

            {/* Right Column */}
            <div className="flex flex-col gap-8 h-full">
                <div className="flex-[1]">
                    <TaskInfo task={task} reasoning={reasoning} />
                </div>
                <div className="flex-[4]">
                    <AgentPlanning plan={plan} thought={thought} code={code} />
                </div>
      </div>
        </main>
      </div>
  );
}

export default App;
