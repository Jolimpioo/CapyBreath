import { useState, useEffect, useCallback } from 'react';
import type { FaseSessao } from '../types/breathing.types';
import {
  RESPIRACOES_PADRAO,
  TEMPO_INSPIRACAO,
  TEMPO_EXPIRACAO,
  TEMPO_RECUPERACAO,
} from '../constants/breathing.constants';

/**
 * Custom Hook para gerenciar uma sessão de respiração Wim Hof
 *
 * Fluxo:
 * 1. RESPIRAÇÃO: 30 ciclos de inspirar (2s) + expirar (2s)
 * 2. RETENÇÃO: Segurar respiração até o usuário decidir parar
 * 3. RECUPERAÇÃO: Inspirar e segurar por 15s
 * 4. FINALIZADA: Mostra resultado
 */
export function useBreathingSession() {
  // Estados principais
  const [fase, setFase] = useState<FaseSessao>('inicio');
  const [respiracaoAtual, setRespiracaoAtual] = useState(0);
  const [tempoRetencao, setTempoRetencao] = useState(0);
  const [tempoRetencaoFinal, setTempoRetencaoFinal] = useState(0); // NOVO: salva o tempo final
  const [pausada, setPausada] = useState(false);
  const [isInhaling, setIsInhaling] = useState(false);

  // Tempo do ciclo de respiração (inspirar + expirar)
  const tempoCicloRespiracao = TEMPO_INSPIRACAO + TEMPO_EXPIRACAO;

  /**
   * LÓGICA DA FASE DE RESPIRAÇÃO
   * - Conta de 1 até 30 respirações
   * - Alterna entre inspirar/expirar a cada 2s
   * - Quando chega em 30, vai para retenção
   */
  useEffect(() => {
    if (fase !== 'respiracao' || pausada) return;

    // Timer para alternar inspirar/expirar
    const animationTimer = setInterval(() => {
      setIsInhaling(prev => !prev);
    }, TEMPO_INSPIRACAO);

    // Timer para contar respirações completas
    const countTimer = setInterval(() => {
      setRespiracaoAtual(prev => {
        const proxima = prev + 1;

        // Chegou em 30? Vai para retenção
        if (proxima >= RESPIRACOES_PADRAO) {
          setFase('retencao');
          setIsInhaling(false);
          return prev;
        }

        return proxima;
      });
    }, tempoCicloRespiracao);

    // Cleanup: limpa timers quando muda de fase ou pausa
    return () => {
      clearInterval(animationTimer);
      clearInterval(countTimer);
    };
  }, [fase, pausada, tempoCicloRespiracao]);

  /**
   * LÓGICA DA FASE DE RETENÇÃO
   * - Cronômetro crescente (conta segundos)
   * - Usuário decide quando parar
   */
  useEffect(() => {
    if (fase !== 'retencao' || pausada) return;

    const timer = setInterval(() => {
      setTempoRetencao(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [fase, pausada]);

  /**
   * LÓGICA DA FASE DE RECUPERAÇÃO
   * - Timer decrescente de 15s
   * - Quando chega em 0, finaliza
   */
  useEffect(() => {
    if (fase !== 'recuperacao' || pausada) return;

    // Começa em 15 segundos
    let tempoRestante = TEMPO_RECUPERACAO / 1000;

    const timer = setInterval(() => {
      tempoRestante -= 1;
      setTempoRetencao(tempoRestante);

      // Acabou? Finaliza sessão
      if (tempoRestante <= 0) {
        setFase('finalizada');
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [fase, pausada]);

  /**
   * Inicia uma nova sessão
   */
  const iniciarSessao = useCallback(() => {
    setFase('respiracao');
    setRespiracaoAtual(0);
    setTempoRetencao(0);
    setTempoRetencaoFinal(0);
    setPausada(false);
    setIsInhaling(false);
  }, []);

  /**
   * Pausa/resume a sessão atual
   */
  const togglePausa = useCallback(() => {
    setPausada(prev => !prev);
  }, []);

  /**
   * Para a sessão completamente e volta ao início
   */
  const pararSessao = useCallback(() => {
    setFase('inicio');
    setRespiracaoAtual(0);
    setTempoRetencao(0);
    setTempoRetencaoFinal(0);
    setPausada(false);
    setIsInhaling(false);
  }, []);

  /**
   * Avança para a próxima fase manualmente
   * (usado principalmente na retenção)
   */
  const proximaFase = useCallback(() => {
    if (fase === 'retencao') {
      setTempoRetencaoFinal(tempoRetencao);
      setTempoRetencao(TEMPO_RECUPERACAO / 1000);
      setFase('recuperacao');
      setIsInhaling(true); // Inspirar fundo
    }
  }, [fase, tempoRetencao]);

  // Retorna estado e funções para os componentes
  return {
    // Estado atual
    fase,
    respiracaoAtual,
    totalRespiracoes: RESPIRACOES_PADRAO,
    tempoRetencao,
    tempoRetencaoFinal, // NOVO: tempo salvo da retenção
    pausada,
    isInhaling,

    // Funções de controle
    iniciarSessao,
    togglePausa,
    pararSessao,
    proximaFase,
  };
}
