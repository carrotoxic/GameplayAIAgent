import React from 'react';

const Card = ({ children, className = '' }) => {
  return (
    <div className={`bg-surface rounded-lg shadow-md flex flex-col ${className}`}>
      {children}
    </div>
  );
};

export const CardHeader = ({ children, icon }) => (
    <div className="p-4 border-b border-white/10 flex items-center gap-3">
        {icon}
        <h2 className="text-lg font-bold text-gray-200">{children}</h2>
    </div>
);

export const CardContent = ({ children, className = '' }) => (
    <div className={`p-4 ${className}`}>
        {children}
    </div>
);


export default Card; 