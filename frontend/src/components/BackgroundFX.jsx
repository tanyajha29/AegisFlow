import { motion, useMotionValue, useSpring } from 'framer-motion';
import { useEffect, useMemo } from 'react';

const makeParticles = (count = 14) =>
  Array.from({ length: count }).map((_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 4,
    duration: 6 + Math.random() * 4,
    size: 4 + Math.random() * 4,
  }));

const BackgroundFX = () => {
  const particles = useMemo(() => makeParticles(16), []);
  const mouseX = useMotionValue(typeof window !== 'undefined' ? window.innerWidth / 2 : 0);
  const mouseY = useMotionValue(typeof window !== 'undefined' ? window.innerHeight / 2 : 0);

  const x = useSpring(mouseX, { stiffness: 120, damping: 18, mass: 0.4 });
  const y = useSpring(mouseY, { stiffness: 120, damping: 18, mass: 0.4 });

  useEffect(() => {
    const handler = (e) => {
      mouseX.set(e.clientX);
      mouseY.set(e.clientY);
    };
    window.addEventListener('pointermove', handler);
    return () => window.removeEventListener('pointermove', handler);
  }, [mouseX, mouseY]);

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <motion.div
        className="absolute inset-0 animated-grid opacity-70"
        animate={{ backgroundPositionX: ['0%', '100%'], backgroundPositionY: ['0%', '100%'] }}
        transition={{ duration: 28, repeat: Infinity, ease: 'linear' }}
      />

      <motion.div
        className="radial-blob"
        style={{ top: '-10%', left: '-5%', width: '32rem', height: '32rem' }}
        animate={{ scale: [0.95, 1.05, 0.98], opacity: [0.45, 0.55, 0.5] }}
        transition={{ repeat: Infinity, duration: 12, ease: 'easeInOut' }}
      />
      <motion.div
        className="radial-blob"
        style={{ bottom: '-12%', right: '-8%', width: '28rem', height: '28rem', background: 'radial-gradient(circle, rgba(6,182,212,0.35), transparent 60%)' }}
        animate={{ scale: [1.02, 0.96, 1.04], opacity: [0.4, 0.52, 0.46] }}
        transition={{ repeat: Infinity, duration: 14, ease: 'easeInOut' }}
      />

      {particles.map((p) => (
        <motion.span
          key={p.id}
          className="particle-dot"
          style={{ top: `${p.y}%`, left: `${p.x}%`, width: p.size, height: p.size }}
          animate={{ y: ['0%', '-12%', '0%'], x: ['0%', '3%', '0%'] }}
          transition={{ duration: p.duration, delay: p.delay, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}

      <motion.div
        className="mouse-light"
        style={{ x, y }}
        animate={{ opacity: [0.1, 0.2, 0.1] }}
        transition={{ repeat: Infinity, duration: 4, ease: 'easeInOut' }}
      />
    </div>
  );
};

export default BackgroundFX;
