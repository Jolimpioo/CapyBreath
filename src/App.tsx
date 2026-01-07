import { useBreathingSession } from './hooks/useBreathingSession';
import BreathingCircle from './components/BreathingCircle';
import BreathCounter from './components/BreathCounter';
import Timer from './components/Timer';
import { MENSAGENS } from './constants/breathing.constants';

function App() {
  const {
    fase,
    respiracaoAtual,
    totalRespiracoes,
    tempoRetencao,
    tempoRetencaoFinal,
    pausada,
    isInhaling,
    iniciarSessao,
    togglePausa,
    pararSessao,
    proximaFase,
  } = useBreathingSession();

  // Renderiza tela inicial (antes de começar)
  if (fase === 'inicio') {
    return (
      <div className="min-h-screen bg-gradient-to-b from-capy-secondary to-capy-accent flex flex-col items-center justify-center p-8">
        <h1 className="text-6xl font-bold text-white mb-4 drop-shadow-lg">
          🦫 CapyBreath
        </h1>
        <p className="text-xl text-white/90 mb-12">
          Respiração Consciente e Tranquila
        </p>

        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 max-w-md mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Como Funciona</h2>
          <ul className="space-y-3 text-white/90">
            <li className="flex items-start">
              <span className="mr-3">1️⃣</span>
              <span>30 respirações profundas (inspirar e expirar)</span>
            </li>
            <li className="flex items-start">
              <span className="mr-3">2️⃣</span>
              <span>Retenção: segure até não aguentar mais</span>
            </li>
            <li className="flex items-start">
              <span className="mr-3">3️⃣</span>
              <span>Recuperação: inspire fundo e segure 15s</span>
            </li>
          </ul>
        </div>

        <button
          onClick={iniciarSessao}
          className="px-12 py-5 bg-white text-capy-primary font-bold text-2xl rounded-full hover:bg-white/90 hover:scale-105 transition-all shadow-2xl active:scale-95"
        >
          ▶ Iniciar Sessão
        </button>
      </div>
    );
  }

  // Renderiza tela de sessão ativa
  return (
    <div className="min-h-screen bg-gradient-to-b from-capy-secondary to-capy-accent flex flex-col items-center justify-center p-8">
      {/* Header com título e fase atual */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-lg">
          🦫 CapyBreath
        </h1>
        <p className="text-white/80 text-lg">{MENSAGENS[fase]}</p>
      </div>

      {/* Área principal - muda conforme a fase */}
      <div className="flex-1 flex flex-col items-center justify-center space-y-8 w-full max-w-2xl">
        {/* FASE: RESPIRAÇÃO */}
        {fase === 'respiracao' && (
          <>
            <BreathCounter atual={respiracaoAtual} total={totalRespiracoes} />
            <BreathingCircle isInhaling={isInhaling} fase={fase} />
          </>
        )}

        {/* FASE: RETENÇÃO */}
        {fase === 'retencao' && (
          <>
            <Timer segundos={tempoRetencao} label="Tempo de Retenção" />
            <BreathingCircle isInhaling={false} fase={fase} />
            <button
              onClick={proximaFase}
              className="mt-8 px-8 py-4 bg-white/20 backdrop-blur-sm border-2 border-white/40 text-white font-bold text-xl rounded-full hover:bg-white/30 transition-all"
            >
              Terminar Retenção →
            </button>
          </>
        )}

        {/* FASE: RECUPERAÇÃO */}
        {fase === 'recuperacao' && (
          <>
            <Timer segundos={tempoRetencao} label="Recuperação" />
            <BreathingCircle isInhaling={true} fase={fase} />
            <p className="text-white/80 text-lg">Inspire fundo e segure...</p>
          </>
        )}

        {/* FASE: FINALIZADA */}
        {fase === 'finalizada' && (
          <div className="text-center space-y-6">
            <div className="text-8xl mb-4">🎉</div>
            <h2 className="text-4xl font-bold text-white mb-4">
              Sessão Concluída!
            </h2>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
              <p className="text-white/70 text-sm uppercase tracking-wide mb-2">
                Tempo de Retenção
              </p>
              <Timer segundos={tempoRetencaoFinal} />
            </div>
            <button
              onClick={iniciarSessao}
              className="mt-8 px-10 py-4 bg-white text-capy-primary font-bold text-xl rounded-full hover:bg-white/90 hover:scale-105 transition-all shadow-lg"
            >
              🔄 Nova Sessão
            </button>
          </div>
        )}
      </div>

      {/* Controles (exceto na tela final) */}
      {fase !== 'finalizada' && (
        <div className="mt-8 flex gap-4">
          <button
            onClick={togglePausa}
            className="px-6 py-3 bg-white/20 backdrop-blur-sm border-2 border-white/40 text-white font-semibold rounded-full hover:bg-white/30 transition-all"
          >
            {pausada ? '▶ Retomar' : '⏸ Pausar'}
          </button>
          <button
            onClick={pararSessao}
            className="px-6 py-3 bg-white/20 backdrop-blur-sm border-2 border-white/40 text-white font-semibold rounded-full hover:bg-white/30 transition-all"
          >
            ⏹ Parar
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
