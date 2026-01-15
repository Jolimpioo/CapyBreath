/**
 * Componente visual do círculo de respiração
 * Anima conforme o usuário respira (inspirar/expirar)
 */

interface BreathingCircleProps {
  isInhaling: boolean;
  fase: 'inicio' | 'respiracao' | 'retencao' | 'recuperacao' | 'finalizada';
}

function BreathingCircle({ isInhaling, fase }: BreathingCircleProps) {
  // Define texto baseado na fase
  const getFaseText = () => {
    switch (fase) {
      case 'respiracao':
        return isInhaling ? 'Inspire' : 'Expire';
      case 'retencao':
        return 'Segure';
      case 'recuperacao':
        return 'Segure';
      case 'finalizada':
        return 'Completo!';
      default:
        return '';
    }
  };

  return (
    <div className="flex flex-col items-center justify-center">
      {/* Círculo animado */}
      <div
        className={`
          w-64 h-64 
          rounded-full 
          bg-white/20 
          backdrop-blur-sm
          border-4 border-white/40
          flex flex-col items-center justify-center
          shadow-2xl
          transition-all duration-[2000ms] ease-in-out
          ${isInhaling ? 'scale-125 bg-white/30' : 'scale-100'}
        `}
      >
        <span className="text-6xl mb-2 filter drop-shadow-lg">🦫</span>
        {fase !== 'inicio' && (
          <span className="text-white font-semibold text-lg">
            {getFaseText()}
          </span>
        )}
      </div>
    </div>
  );
}

export default BreathingCircle;
