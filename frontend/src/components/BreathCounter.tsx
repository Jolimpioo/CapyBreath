/**
 * Componente BreathCounter
 * Exibe contagem de respirações atual/total
 * Exemplo: "15 / 30"
 */

interface BreathCounterProps {
  atual: number;
  total: number;
}

function BreathCounter({ atual, total }: BreathCounterProps) {
  // Calcula porcentagem para barra de progresso
  const porcentagem = (atual / total) * 100;

  return (
    <div className="flex flex-col items-center w-full max-w-md">
      {/* Contador numérico */}
      <div className="text-5xl font-bold text-white mb-4">
        <span className="text-6xl">{atual}</span>
        <span className="text-white/60 mx-2">/</span>
        <span className="text-white/80">{total}</span>
      </div>

      {/* Barra de progresso */}
      <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden">
        <div
          className="h-full bg-white transition-all duration-300 ease-out"
          style={{ width: `${porcentagem}%` }}
        />
      </div>

      {/* Label */}
      <p className="text-white/70 text-sm mt-3 uppercase tracking-wide">
        Respirações
      </p>
    </div>
  );
}

export default BreathCounter;
