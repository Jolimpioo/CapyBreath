import { useState } from 'react';
import BreathingCircle from './components/BreathingCircle';

function App() {
  const [isBreathing, setIsBreathing] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-b from-capy-secondary to-capy-accent flex flex-col items-center justify-center p-8">
      {/* Header */}
      <h1 className="text-6xl font-bold text-white mb-2 drop-shadow-lg">
        🦫 CapyBreath
      </h1>
      <p className="text-white/80 mb-12 text-lg">
        Técnica de Respiração Guiada
      </p>
      
      {/* Círculo de Respiração */}
      <BreathingCircle isBreathing={isBreathing} />
      
      {/* Botão de Controle */}
      <button
        onClick={() => setIsBreathing(!isBreathing)}
        className="mt-12 px-8 py-4 bg-white text-capy-primary font-bold text-xl rounded-full hover:bg-white/90 hover:scale-105 transition-all shadow-lg active:scale-95"
      >
        {isBreathing ? '⏸ Parar' : '▶ Iniciar'}
      </button>
      
      {/* Instrução */}
      <p className="mt-6 text-white/70 text-sm">
        {isBreathing ? 'Acompanhe a animação' : 'Clique para começar'}
      </p>
    </div>
  );
}

export default App;