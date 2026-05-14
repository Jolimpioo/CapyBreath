import { useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useBreathingSession } from './hooks/useBreathingSession';
import Navbar from './components/Navbar';
import BreathingCircle from './components/BreathingCircle';
import BreathCounter from './components/BreathCounter';
import Timer from './components/Timer';
import {
  PhaseActionButton,
  SessionHero,
  SessionPanel,
} from './components/session/SessionLayout';
import { createSession } from './api/sessionApi';
import { getApiErrorMessage } from './api/apiError';
import { useAuthContext } from './features/auth/AuthProvider';
import {
  MENSAGENS,
  TEMPO_EXPIRACAO,
  TEMPO_INSPIRACAO,
  TEMPO_RECUPERACAO,
} from './constants/breathing.constants';
import { saveAnonymousSession } from './utils/localSessionStorage';
import type {
  SessionCreateRequest,
  SessionUnlockedAchievement,
} from './types/session.types';

function App() {
  const {
    fase,
    roundAtual,
    totalRounds,
    retencoesPorRound,
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
  const { isAuthenticated, showToast } = useAuthContext();
  const [savingSession, setSavingSession] = useState(false);
  const [sessionSaved, setSessionSaved] = useState(false);
  const [sessionSavedLocally, setSessionSavedLocally] = useState(false);
  const [sessionError, setSessionError] = useState<string | null>(null);
  const [newAchievements, setNewAchievements] = useState<
    SessionUnlockedAchievement[]
  >([]);
  const [sessionGroupId, setSessionGroupId] = useState(() =>
    crypto.randomUUID()
  );
  const handledFinalizationRef = useRef(false);

  const sessionPayloads = useMemo<SessionCreateRequest[]>(() => {
    if (fase !== 'finalizada' || retencoesPorRound.length === 0) {
      return [];
    }

    const breathingDurationSeconds =
      totalRespiracoes * ((TEMPO_INSPIRACAO + TEMPO_EXPIRACAO) / 1000);

    return retencoesPorRound
      .map((retencao, index) => ({
        retencao,
        roundNumber: index + 1,
      }))
      .filter(round => round.retencao > 0)
      .map(round => ({
        session_group_id: sessionGroupId,
        round_number: round.roundNumber,
        total_rounds: totalRounds,
        breaths_count: totalRespiracoes,
        retention_time: round.retencao,
        recovery_time: TEMPO_RECUPERACAO / 1000,
        duration_seconds:
          breathingDurationSeconds +
          round.retencao +
          TEMPO_RECUPERACAO / 1000,
        technique_variant: 'standard',
      }));
  }, [
    fase,
    retencoesPorRound,
    sessionGroupId,
    totalRespiracoes,
    totalRounds,
  ]);

  useEffect(() => {
    if (fase !== 'finalizada') {
      handledFinalizationRef.current = false;
      setSavingSession(false);
      return;
    }

    if (!sessionPayloads.length || handledFinalizationRef.current) {
      return;
    }

    handledFinalizationRef.current = true;

    const persistSession = async () => {
      setSavingSession(true);
      setSessionError(null);
      setSessionSaved(false);
      setSessionSavedLocally(false);
      setNewAchievements([]);

      if (!isAuthenticated) {
        sessionPayloads.forEach(payload => saveAnonymousSession(payload));
        setSessionSavedLocally(true);
        setSavingSession(false);
        showToast('Rounds salvos temporariamente neste dispositivo.', 'info');
        return;
      }

      try {
        const responses = await Promise.all(
          sessionPayloads.map(payload => createSession(payload))
        );
        const unlockedMap = new Map<string, SessionUnlockedAchievement>();
        responses.forEach(response => {
          response.newly_unlocked.forEach(achievement => {
            unlockedMap.set(achievement.achievement_id, achievement);
          });
        });
        const unlockedNow = Array.from(unlockedMap.values());

        setSessionSaved(true);
        setNewAchievements(unlockedNow);
        showToast('Sessão com rounds salva no seu histórico!', 'success');
      } catch (error) {
        const message = getApiErrorMessage(
          error,
          'Não foi possível salvar sua sessão agora.'
        );
        setSessionError(message);
        showToast(message, 'error');
      } finally {
        setSavingSession(false);
      }
    };

    void persistSession();
  }, [fase, isAuthenticated, sessionPayloads, showToast]);

  const handleStartSession = () => {
    setSessionSaved(false);
    setSessionSavedLocally(false);
    setSessionError(null);
    setNewAchievements([]);
    setSessionGroupId(crypto.randomUUID());
    iniciarSessao();
  };

  // Renderiza tela inicial (antes de começar)
  if (fase === 'inicio') {
    return (
      <div className="min-h-screen overflow-x-hidden bg-gradient-to-b from-capy-secondary to-capy-accent flex flex-col">
        <Navbar />
        <div className="flex flex-col items-center justify-center flex-1 p-8">
          <SessionHero
            title="🦫 CapyBreath"
            subtitle="Respiração Consciente e Tranquila"
          />

          <SessionPanel className="mb-8 w-full max-w-md">
            <h2 className="mb-4 text-2xl font-bold text-white">
              Como Funciona
            </h2>
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
              <li className="flex items-start">
                <span className="mr-3">🔁</span>
                <span>3 rounds por sessão (padrão)</span>
              </li>
            </ul>
          </SessionPanel>

          <PhaseActionButton
            onClick={handleStartSession}
            className="px-12 py-5 text-2xl font-bold shadow-2xl hover:scale-105 active:scale-95"
          >
            ▶ Iniciar Sessão
          </PhaseActionButton>
        </div>
      </div>
    );
  }

  // Renderiza tela de sessão ativa
  return (
    <div className="min-h-screen overflow-x-hidden bg-gradient-to-b from-capy-secondary to-capy-accent flex flex-col items-center justify-center p-8">
      <SessionHero
        title="🦫 CapyBreath"
        subtitle={MENSAGENS[fase]}
        roundInfo={
          fase !== 'finalizada'
            ? `Round ${roundAtual} de ${totalRounds}`
            : undefined
        }
      />

      <div className="flex-1 flex flex-col items-center justify-center space-y-8 w-full max-w-2xl">
        {fase === 'respiracao' && (
          <>
            <BreathCounter atual={respiracaoAtual} total={totalRespiracoes} />
            <BreathingCircle isInhaling={isInhaling} fase={fase} />
          </>
        )}

        {fase === 'retencao' && (
          <>
            <Timer segundos={tempoRetencao} label="Tempo de Retenção" />
            <BreathingCircle isInhaling={false} fase={fase} />
            <PhaseActionButton
              onClick={proximaFase}
              variant="ghost"
              className="mt-8 text-xl font-bold"
            >
              Terminar Retenção →
            </PhaseActionButton>
          </>
        )}

        {fase === 'recuperacao' && (
          <>
            <Timer segundos={tempoRetencao} label="Recuperação" />
            <BreathingCircle isInhaling={true} fase={fase} />
            <p className="text-white/80 text-lg">Inspire fundo e segure...</p>
          </>
        )}

        {fase === 'finalizada' && (
          <div className="text-center space-y-6 w-full">
            <div className="text-8xl mb-4">🎉</div>
            <h2 className="text-4xl font-bold text-white mb-4">
              Sessão Concluída!
            </h2>
            <SessionPanel>
              <p className="mb-2 text-sm uppercase tracking-wide text-white/70">
                Tempo de Retenção
              </p>
              <Timer segundos={tempoRetencaoFinal} />
              <p className="mt-2 text-white/70">
                {retencoesPorRound.length} de {totalRounds} rounds concluídos
              </p>
            </SessionPanel>

            {retencoesPorRound.length > 0 && (
              <SessionPanel className="mx-auto max-w-xl text-left">
                <h3 className="text-white font-semibold mb-3">
                  Retenção por round
                </h3>
                <ul className="space-y-2">
                  {retencoesPorRound.map((valor, index) => (
                    <li
                      key={`round-${index + 1}`}
                      className="flex justify-between text-white/90"
                    >
                      <span>Round {index + 1}</span>
                      <span className="font-bold">{valor}s</span>
                    </li>
                  ))}
                </ul>
              </SessionPanel>
            )}

            <SessionPanel className="mx-auto max-w-xl text-left text-white shadow-lg">
              <h3 className="text-xl font-bold mb-3">Resumo da sessão</h3>

              {savingSession && (
                <p className="text-white/90">Salvando sua sessão...</p>
              )}

              {!savingSession && sessionSaved && (
                <p className="text-emerald-200 font-medium">
                  Sessão salva no seu histórico com sucesso.
                </p>
              )}

              {!savingSession && sessionSavedLocally && (
                <div className="space-y-3">
                  <p className="text-amber-100 font-medium">
                    Sessão salva temporariamente neste dispositivo.
                  </p>
                  <p className="text-white/80 text-sm">
                    Faça login ou crie sua conta para migrar essa sessão
                    automaticamente e manter seu histórico.
                  </p>
                  <div className="flex flex-wrap gap-3 pt-1">
                    <Link
                      to="/login"
                      className="min-h-[44px] rounded-full bg-white px-4 py-2 text-capy-primary font-semibold hover:bg-white/90 transition inline-flex items-center"
                    >
                      Entrar
                    </Link>
                    <Link
                      to="/register"
                      className="min-h-[44px] rounded-full border border-white/50 px-4 py-2 text-white font-semibold hover:bg-white/10 transition inline-flex items-center"
                    >
                      Criar conta
                    </Link>
                  </div>
                </div>
              )}

              {!savingSession && sessionError && (
                <p className="text-red-200 font-medium">{sessionError}</p>
              )}

              {!savingSession &&
                isAuthenticated &&
                newAchievements.length > 0 && (
                  <div className="mt-4 rounded-xl bg-emerald-500/20 border border-emerald-300/30 p-4">
                    <p className="font-bold text-emerald-100 mb-3">
                      🏆 Novas conquistas desbloqueadas
                    </p>
                    <ul className="space-y-2">
                      {newAchievements.map(achievement => (
                        <li
                          key={achievement.achievement_id}
                          className="rounded-lg bg-black/10 p-3"
                        >
                          <div className="font-semibold">
                            {achievement.icon} {achievement.name}
                          </div>
                          <div className="text-sm text-white/80">
                            {achievement.description}
                          </div>
                          <div className="text-xs text-emerald-100 mt-1">
                            +{achievement.points} pts • {achievement.rarity}
                          </div>
                        </li>
                      ))}
                    </ul>
                    <Link
                      to="/achievements"
                      className="mt-4 inline-flex min-h-[44px] items-center rounded-full bg-white px-4 py-2 text-capy-primary font-semibold hover:bg-white/90 transition"
                    >
                      Ver conquistas
                    </Link>
                  </div>
                )}
            </SessionPanel>

            <PhaseActionButton
              onClick={handleStartSession}
              className="mt-4 px-10 py-4 text-xl font-bold shadow-lg hover:scale-105"
            >
              🔄 Nova Sessão
            </PhaseActionButton>
          </div>
        )}
      </div>

      {fase !== 'finalizada' && (
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <PhaseActionButton onClick={togglePausa} variant="ghost">
            {pausada ? '▶ Retomar' : '⏸ Pausar'}
          </PhaseActionButton>
          <PhaseActionButton onClick={pararSessao} variant="ghost">
            ⏹ Parar
          </PhaseActionButton>
        </div>
      )}
    </div>
  );
}

export default App;
