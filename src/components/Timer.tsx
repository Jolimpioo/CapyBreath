/**
 * Componente Timer
 * Exibe tempo em formato MM:SS
 * Usado nas fases de retenção e recuperação
 */

interface TimerProps {
  segundos: number;
  label?: string;
}

function Timer({ segundos, label }: TimerProps) {
  /**
   * Formata segundos para MM:SS
   * Exemplo: 65 segundos → "01:05"
   */
  const formatarTempo = (segs: number): string => {
    const minutos = Math.floor(segs / 60);
    const segundosRestantes = segs % 60;

    return `${minutos.toString().padStart(2, '0')}:${segundosRestantes.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col items-center">
      {label && (
        <p className="text-white/70 text-sm mb-2 uppercase tracking-wide">
          {label}
        </p>
      )}
      <div className="text-7xl font-bold text-white font-mono tracking-wider drop-shadow-lg">
        {formatarTempo(segundos)}
      </div>
    </div>
  );
}

export default Timer;
