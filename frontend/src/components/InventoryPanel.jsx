import React, { useState, useEffect } from 'react';
import Card, { CardContent } from './Card';

const InventoryPanel = ({ isStarted }) => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (!isStarted) return;

    const pollInventory = async () => {
      try {
        const response = await fetch('/inventory');
        if (response.ok) {
          setIsReady(true);
          return; // Stop polling
        }
      } catch (error) {
        // Network error, inventory probably not up yet
        console.log("InventoryPanel not ready, will retry...");
      }
      setTimeout(pollInventory, 2000); // Retry after 2 seconds
    };

    pollInventory();
  }, [isStarted]);

  return (
    <Card className="flex flex-col h-full">
      <CardContent className="flex-grow p-0.5 overflow-hidden">
        {isReady ? (
          <iframe
            src="/inventory"
            title="Inventory"
            className="w-[110.33%] h-[110.33%] rounded-b-lg border-none scale-[0.75] origin-top-left"
            scrolling="no"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-background rounded-b-lg">
            <p className="text-on-background">Connecting to Inventory...</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default InventoryPanel; 