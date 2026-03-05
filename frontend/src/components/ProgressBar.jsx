import React from 'react';

const ProgressBar = ({ value }) => (
  <div className="w-full bg-surface border border-border rounded-full h-2 overflow-hidden">
    <div
      className="h-full bg-gradient-to-r from-cyber via-accent to-cyber transition-all"
      style={{ width: `${value}%` }}
    />
  </div>
);

export default ProgressBar;
