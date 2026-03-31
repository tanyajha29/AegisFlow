const GlassCard = ({ children, className = '' }) => (
  <div
    className={`glass-card rounded-2xl transition-all ${className}`}
  >
    {children}
  </div>
);

export default GlassCard;
