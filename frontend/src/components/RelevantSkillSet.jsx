import React from 'react';
import Card, { CardHeader, CardContent } from './Card';

const RelevantSkillSet = ({ skills }) => {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader>Relevant Skill Set</CardHeader>
      <CardContent className="overflow-auto flex-grow">
        {skills && skills.length > 0 ? (
          <ul className="space-y-2">
            {skills.map((skill, index) => (
              <li key={index} className="bg-gray-800 p-2 rounded">
                <p className="font-semibold p-2 rounded text-sm text-green-400">{skill.name || `Skill ${index + 1}`}</p>
                <p className="text-xs text-gray-400">{skill.description}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No relevant skills found.</p>
        )}
      </CardContent>
    </Card>
  );
};

export default RelevantSkillSet; 