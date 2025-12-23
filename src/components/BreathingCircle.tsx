/**
 * Componente visual do círculo de respiração
 * Anima conforme o usuário respira
 */

interface BreathingCircleProps {
  isBreathing: boolean;
}

function BreathingCircle({ isBreathing }: BreathingCircleProps) {
  return (
    <div className="flex items-center justify-center">
      <div 
        className={`
          w-64 h-64 
          rounded-full 
          bg-white/20 
          backdrop-blur-sm
          border-4 border-white/40
          flex items-center justify-center
          shadow-2xl
          transition-all duration-[2000ms] ease-in-out
          ${isBreathing ? 'scale-125 bg-white/30' : 'scale-100'}
        `}
      >
        <span className="text-6xl filter drop-shadow-lg">
          🦫
        </span>
      </div>
    </div>
  );
}

export default BreathingCircle;