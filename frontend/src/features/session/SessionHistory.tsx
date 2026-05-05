import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getSessions } from '../../api/sessionApi';
import type { SessionListItem } from '../../types/session.types';
import { getApiErrorMessage } from '../../api/apiError';
import Button from '../../components/ui/Button';
import Alert from '../../components/ui/Alert';
import PageContainer from '../../components/ui/PageContainer';
import Card from '../../components/ui/Card';

type SessionHistoryItemProps = {
  session: SessionListItem;
};

const SessionHistoryItem = ({ session }: SessionHistoryItemProps) => (
  <li>
    <Link
      to={`/session/${session.id}`}
      className="block rounded-lg border border-transparent p-3 transition hover:border-capy-secondary/40 hover:bg-capy-light/40 focus-visible:border-capy-accent focus-visible:bg-capy-light/50"
    >
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <span className="font-mono text-xs text-gray-500">
          {new Date(session.session_date).toLocaleString('pt-BR')}
        </span>

        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm">
            Retenção: <b>{session.retention_time}s</b>
          </span>
          <span className="rounded-full border border-capy-secondary/45 px-2 py-1 text-xs">
            Técnica: {session.technique_variant}
          </span>
          {session.is_personal_best && (
            <span className="rounded-full border border-amber-300 bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-800">
              🏆 Personal Best
            </span>
          )}
        </div>
      </div>
    </Link>
  </li>
);

const EmptyState = ({ text }: { text: string }) => (
  <p className="text-gray-600">{text}</p>
);

const SessionHistory = () => {
  const [sessions, setSessions] = useState<SessionListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSessions() {
      setLoading(true);
      setError(null);
      try {
        const data = await getSessions({ page, size: 10 });
        setSessions(data.items);
        setPages(data.pages);
      } catch (error) {
        setSessions([]);
        setError(
          getApiErrorMessage(error, 'Erro ao carregar histórico de sessões.')
        );
      } finally {
        setLoading(false);
      }
    }
    void fetchSessions();
  }, [page]);

  return (
    <PageContainer className="max-w-3xl mt-2">
      <Card>
        <h1 className="mb-4 text-2xl font-bold">Histórico de Sessões</h1>

        {loading ? (
          <p>Carregando sessões...</p>
        ) : error ? (
          <Alert variant="error">{error}</Alert>
        ) : sessions.length === 0 ? (
          <EmptyState text="Nenhuma sessão encontrada." />
        ) : (
          <>
            <ul className="space-y-2">
              {sessions.map(session => (
                <SessionHistoryItem key={session.id} session={session} />
              ))}
            </ul>

            <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setPage(prev => Math.max(1, prev - 1))}
                disabled={page <= 1}
              >
                Anterior
              </Button>

              <span className="text-sm">
                Página {page} de {pages}
              </span>

              <Button
                type="button"
                variant="ghost"
                onClick={() => setPage(prev => Math.min(pages, prev + 1))}
                disabled={page >= pages}
              >
                Próxima
              </Button>
            </div>
          </>
        )}
      </Card>
    </PageContainer>
  );
};

export default SessionHistory;
