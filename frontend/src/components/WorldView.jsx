import React, { useState, useEffect } from 'react';
import Card, { CardContent } from './Card';

const WorldView = ({ isStarted }) => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (!isStarted) return;

    const pollViewer = async () => {
      try {
        const response = await fetch('/viewer');
        if (response.ok) {
          setIsReady(true);
          return; // Stop polling
        }
      } catch (error) {
        // Network error, viewer probably not up yet
        console.log("WorldView not ready, will retry...");
      }
      setTimeout(pollViewer, 2000); // Retry after 2 seconds
    };

    pollViewer();
  }, [isStarted]);

  return (
    <Card className="flex-grow h-full">
      <CardContent className="p-1 flex-grow">
        {isReady ? (
          <iframe
            src="/viewer"
            title="World View"
            className="w-full h-full rounded-b-lg border-none"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-background rounded-b-lg">
            <p className="text-on-background">Connecting to World View...</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default WorldView; 