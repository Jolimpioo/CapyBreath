/**
 * Tipos TypeScript para o CapyBreath
 */

// Fases possíveis da sessão de respiração
export type FaseSessao = 
  | 'inicio'
  | 'respiracao' 
  | 'retencao' 
  | 'recuperacao' 
  | 'finalizada';

// Estado completo de uma sessão
export interface EstadoSessao {
  fase: FaseSessao;
  respiracaoAtual: number;
  totalRespiracoes: number;
  tempoRetencao: number;
  pausada: boolean;
}

// Configurações da sessão
export interface ConfiguracaoSessao {
  numeroRespiracoes: number;
  tempoRecuperacao: number;
  somAtivado: boolean;
}

// Resultado de uma sessão completa
export interface ResultadoSessao {
  tempoRetencao: number;
  dataHora: Date;
}