import React from 'react';

const GlassCard = ({ children, className = '' }) => (
  <div className={`glass rounded-2xl border border-border shadow-glass ${className}`}>
    {children}
  </div>
);

export default GlassCard;
