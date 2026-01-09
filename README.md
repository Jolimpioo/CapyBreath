# 🦫 CapyBreath

> **Aplicação web de respiração guiada baseada na técnica Wim Hof**

Aplicação progressiva (PWA) para prática da técnica de respiração Wim Hof, oferecendo uma experiência visual e interativa para meditação e controle respiratório.

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Técnica Wim Hof](#técnica-wim-hof)
- [Stack Tecnológica](#stack-tecnológica)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Arquitetura](#arquitetura)
- [Roadmap](#roadmap)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## 🎯 Sobre o Projeto

O **CapyBreath** é uma aplicação web moderna desenvolvida para guiar usuários através da técnica de respiração Wim Hof de forma intuitiva e visual. O projeto combina práticas de respiração consciente com uma interface limpa e animações suaves, tornando a experiência acessível tanto para iniciantes quanto para praticantes avançados.

### Motivação

A técnica de respiração Wim Hof tem demonstrado benefícios comprovados para:
- Redução de estresse e ansiedade
- Melhora do sistema imunológico
- Aumento de energia e foco
- Melhor qualidade do sono
- Maior controle sobre resposta ao estresse

Este projeto foi criado para tornar essa prática mais acessível através de uma interface digital moderna.

---

## ✨ Funcionalidades

### Implementadas (MVP v1.0)

- ✅ **Sessão Completa Automática**
  - 30 respirações guiadas (inspirar 2s + expirar 2s)
  - Fase de retenção com cronômetro crescente
  - Fase de recuperação com timer de 15 segundos
  - Tela de resultado com tempo total de retenção

- ✅ **Feedback Visual**
  - Círculo animado sincronizado com a respiração
  - Contador de respirações com barra de progresso (X/30)
  - Timer em formato MM:SS
  - Indicadores visuais de cada fase

- ✅ **Controles de Sessão**
  - Pausar/Retomar sessão a qualquer momento
  - Parar e voltar ao início
  - Avançar manualmente para próxima fase (na retenção)

- ✅ **Interface Responsiva**
  - Design adaptável para desktop, tablet e mobile
  - Tema visual calmante (degradê bege/verde)
  - Animações suaves com CSS transitions

### Em Desenvolvimento

- 🔄 Modal de avisos de segurança
- 🔄 Sons e vibrações de feedback
- 🔄 Personalização de tempos e ciclos
- 🔄 Histórico de sessões
- 🔄 Gráficos de progresso
- 🔄 PWA (instalável)

---

## 🧘 Técnica Wim Hof

A técnica de respiração Wim Hof consiste em três fases principais:

### 1. Respiração (30 ciclos)
- **Inspiração profunda** pelo nariz ou boca (2 segundos)
- **Expiração relaxada** sem forçar (2 segundos)
- Repetir 30 vezes

### 2. Retenção
- Após a última expiração, **segurar a respiração**
- Manter até sentir necessidade de respirar
- Tempo varia de acordo com a prática individual

### 3. Recuperação
- **Inspirar profundamente** e prender o ar
- Segurar por **15 segundos**
- Expirar e relaxar

### ⚠️ Avisos de Segurança

- Sempre pratique **sentado ou deitado**
- **Nunca** pratique na água
- **Nunca** pratique enquanto dirige
- Pare se sentir **tonturas excessivas**
- Consulte um médico se tiver **condições cardíacas**

---

## 🛠️ Stack Tecnológica

### Frontend
- **React 18.3** - Biblioteca para interfaces de usuário
- **TypeScript 5.6** - Tipagem estática
- **Vite 7.x** - Build tool e dev server
- **Tailwind CSS 3.4** - Framework CSS utility-first

### Ferramentas de Desenvolvimento
- **ESLint** - Linting de código
- **Prettier** - Formatação automática
- **Git** - Controle de versão

### Arquitetura
- **Custom Hooks** - Lógica reutilizável
- **Component-based** - Componentização modular
- **State Machine** - Máquina de estados para fases

---

## 📦 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Node.js** (versão 18 ou superior)
- **npm** (geralmente vem com Node.js)
- **Git** (para clonar o repositório)

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/capybreath.git
cd capybreath
```

### 2. Instale as dependências

```bash
npm install
```

### 3. Execute o projeto em modo de desenvolvimento

```bash
npm run dev
```

A aplicação estará disponível em `http://localhost:5173`

### 4. Build para produção

```bash
npm run build
```

Os arquivos otimizados estarão na pasta `dist/`

### 5. Preview da build de produção

```bash
npm run preview
```

---

## 💡 Como Usar

### Iniciando uma Sessão

1. **Acesse a aplicação** no navegador
2. Clique no botão **"▶ Iniciar Sessão"**
3. **Acompanhe a animação** do círculo:
   - Círculo cresce = Inspire
   - Círculo diminui = Expire
4. **Contador automático** mostra progresso (1/30, 2/30...)
5. Após 30 respirações, entra automaticamente na **fase de retenção**

### Fase de Retenção

1. **Segure a respiração** pelo máximo de tempo confortável
2. **Timer conta** os segundos (00:00, 00:01...)
3. Quando não aguentar mais, clique **"Terminar Retenção →"**

### Fase de Recuperação

1. **Inspire profundamente** quando entrar nesta fase
2. **Segure por 15 segundos** (timer decrescente)
3. Aplicação finaliza automaticamente

### Tela Final

- Veja seu **tempo de retenção**
- Clique **"🔄 Nova Sessão"** para recomeçar

### Controles Durante a Sessão

- **⏸ Pausar** - Congela a sessão
- **▶ Retomar** - Continua de onde parou
- **⏹ Parar** - Cancela e volta ao início

---

## 📁 Estrutura do Projeto

```
capybreath/
├── public/                 # Arquivos públicos estáticos
├── src/
│   ├── components/         # Componentes React
│   │   ├── BreathingCircle.tsx
│   │   ├── BreathCounter.tsx
│   │   └── Timer.tsx
│   ├── hooks/              # Custom Hooks
│   │   └── useBreathingSession.ts
│   ├── types/              # Tipos TypeScript
│   │   └── breathing.types.ts
│   ├── constants/          # Constantes da aplicação
│   │   └── breathing.constants.ts
│   ├── utils/              # Funções utilitárias (futuro)
│   ├── App.tsx             # Componente principal
│   ├── main.tsx            # Ponto de entrada
│   └── index.css           # Estilos globais
├── .gitignore
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

---

## 🏗️ Arquitetura

### Máquina de Estados

A aplicação utiliza uma máquina de estados para gerenciar as fases da sessão:

```
início → respiração → retenção → recuperação → finalizada
```

### Custom Hook: `useBreathingSession`

Gerencia toda a lógica da sessão:

```typescript
const {
  fase,                  // Fase atual
  respiracaoAtual,       // Contador de respirações
  tempoRetencao,         // Tempo de retenção atual
  tempoRetencaoFinal,    // Tempo total da retenção
  pausada,               // Estado de pausa
  isInhaling,            // Inspirando ou expirando
  iniciarSessao,         // Função para iniciar
  togglePausa,           // Pausar/retomar
  pararSessao,           // Parar sessão
  proximaFase            // Avançar manualmente
} = useBreathingSession();
```

### Componentes Principais

#### `BreathingCircle`
- Círculo animado que cresce/diminui
- Sincronizado com inspiração/expiração
- Mostra texto da fase atual

#### `BreathCounter`
- Exibe contagem (X/30)
- Barra de progresso visual
- Atualiza automaticamente

#### `Timer`
- Formato MM:SS
- Usado em retenção e recuperação
- Label customizável

### Fluxo de Dados

```
useBreathingSession (Estado)
        ↓
    App.tsx (Orquestração)
        ↓
Componentes (Apresentação)
```

**Princípio:** Unidirectional Data Flow (dados fluem em uma direção)

---

## 🗺️ Roadmap

### Versão 1.1 (Em breve)
- [ ] Modal de avisos de segurança na primeira utilização
- [ ] Sons de feedback (sino/bip)
- [ ] Vibração háptica em dispositivos móveis
- [ ] Melhorias nas animações

### Versão 1.2
- [ ] Painel de configuração (personalizar tempos)
- [ ] Presets (Iniciante, Padrão, Avançado)
- [ ] Salvar preferências no localStorage

### Versão 2.0
- [ ] Histórico de sessões
- [ ] Gráficos de progresso (Chart.js)
- [ ] Estatísticas (melhor tempo, total de sessões)
- [ ] PWA (instalável como app)

### Versão 3.0
- [ ] Backend (Node.js + Express)
- [ ] Autenticação de usuários
- [ ] Sincronização multi-dispositivo
- [ ] Desafios e conquistas
- [ ] Compartilhamento social

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feat/nova-feature`)
3. Commit suas mudanças usando [Conventional Commits](https://www.conventionalcommits.org/)
4. Push para a branch (`git push origin feat/nova-feature`)
5. Abra um Pull Request

### Padrão de Commits

Seguimos o padrão **Conventional Commits**:

```
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação
refactor: refatoração
test: testes
chore: tarefas de manutenção
```

Exemplo:
```bash
git commit -m "feat(timer): add sound notification on completion"
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

Desenvolvido por [Seu Nome]

- GitHub: [@Jolimpioo](https://github.com/Jolimpioo)
- LinkedIn: [José Olimpio](https://www.linkedin.com/in/joseolimpiodemeloneto/)

---

## 📚 Referências

- [Wim Hof Method Official](https://www.wimhofmethod.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Vite Guide](https://vitejs.dev/guide/)
