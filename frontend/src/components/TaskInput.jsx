import React, { useState } from 'react';
import Card, { CardContent, CardHeader, CardTitle } from './Card';
import { startAgent } from '../services/api';

const TaskInput = () => {
  const [task, setTask] = useState('');

  const handleStart = async () => {
    try {
      await startAgent(task);
      console.log('Agent started with task:', task);
    } catch (error) {
      console.error('Failed to start agent:', error);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Task Input</CardTitle>
      </CardHeader>
      <CardContent className="flex gap-2">
        <input
          type="text"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="Enter your task..."
          className="flex-grow p-2 border rounded"
        />
        <button onClick={handleStart} className="px-4 py-2 bg-blue-500 text-white rounded">
          Start
        </button>
      </CardContent>
    </Card>
  );
};

export default TaskInput; 