import React from 'react';
import Card, { CardHeader, CardContent } from './Card';

const PlanningIcon = () => <span className="text-primary">🧠</span>;

const AgentPlanning = ({ plan, thought, code }) => {
    return (
        <Card className="flex-grow h-full">
            <CardHeader icon={<PlanningIcon />}>Agent Planning</CardHeader>
            <CardContent className="space-y-4 flex-grow">
                <div className="h-2/4">
                    <h3 className="font-bold text-gray-400 mb-1">Plan</h3>
                    <p className="text-gray-200 whitespace-pre-line">{plan || 'The agent has not generated a plan yet.'}</p>
                </div>
                <div className="h-1/4 border-t border-white/10 pt-4">
                    <h3 className="font-bold text-gray-400 mb-1">Thought</h3>
                    <p className="text-gray-200 whitespace-pre-line">{thought || 'The agent has not generated a thought yet.'}</p>
                </div>
                <div className="h-1/4 border-t border-white/10 pt-4">
                    <h3 className="font-bold text-gray-400 mb-1">Executing Code</h3>
                    <pre className="bg-gray-800 p-2 rounded text-sm text-green-400">
                        <code>{code || 'No code generated yet.'}</code>
                    </pre>
                </div>
            </CardContent>
        </Card>
    );
};

export default AgentPlanning; 