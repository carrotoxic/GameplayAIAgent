import React from 'react';
import Card, { CardHeader, CardContent } from './Card';

const TaskIcon = () => <span className="text-primary">🎯</span>;

const TaskInfo = ({ task, reasoning }) => {
    return (
        <Card className="flex-grow h-full">
            <CardHeader icon={<TaskIcon />}>Current Task</CardHeader>
            <CardContent className="space-y-4 flex-grow h-full">
                <div>
                    <h3 className="font-bold text-gray-400 mb-1">Task</h3>
                    <p className="text-gray-200">{task || 'Waiting for task...'}</p>
                </div>
                <div className="border-t border-white/10 pt-4">
                    <h3 className="font-bold text-gray-400 mb-1">Reasoning</h3>
                    <p className="text-gray-300">{reasoning || 'No reasoning provided.'}</p>
                </div>
            </CardContent>
        </Card>
    );
};

export default TaskInfo; 