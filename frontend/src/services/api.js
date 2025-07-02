const API_BASE_URL = ''; // Use relative URL to proxy through the FastAPI backend

/**
 * Sends a request to start the agent.
 * @returns {Promise<any>} The response from the server.
 */
export const startAgent = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error('Failed to start agent');
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to start agent:", error);
        throw error;
    }
};

/**
 * Sends a request to reset the agent.
 * @returns {Promise<any>} The response from the server.
 */
export const resetAgent = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/reset`, { method: 'POST' });
        if (!response.ok) {
            throw new Error('Failed to reset agent');
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to reset agent:", error);
        throw error;
    }
};

export const stopAgent = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/stop`, {
            method: 'POST',
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to stop agent');
        }
        return await response.json();
    } catch (error) {
        console.error('Error stopping agent:', error);
        throw error;
    }
}; 