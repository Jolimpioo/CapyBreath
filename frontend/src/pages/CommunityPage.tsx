import { useEffect, useState } from 'react';
import { getApiErrorMessage } from '../api/apiError';
import {
  getLeaderboardByActive,
  getLeaderboardByRetention,
  getLeaderboardByStreak,
  searchUsers,
} from '../api/userApi';
import type { PublicUserStats, User } from '../types/user.types';
import { useAuthContext } from '../features/auth/AuthProvider';
import PageContainer from '../components/ui/PageContainer';
import Card from '../components/ui/Card';
import Alert from '../components/ui/Alert';
import Button from '../components/ui/Button';

type LeaderboardCardProps = {
  title: string;
  items: PublicUserStats[];
  metric: (item: PublicUserStats) => string;
};

const rankTone = (index: number) => {
  if (index === 0) return 'border-capy-accent bg-green-50';
  if (index === 1) return 'border-capy-secondary/50 bg-capy-light/40';
  if (index === 2) return 'border-capy-secondary/35 bg-white';
  return 'border-gray-200 bg-white';
};

const EmptyState = ({ text }: { text: string }) => <p className="text-gray-600">{text}</p>;

const LeaderboardCard = ({ title, items, metric }: LeaderboardCardProps) => (
  <Card compact>
    <h2 className="mb-3 text-xl font-semibold">{title}</h2>
    {items.length === 0 ? (
      <EmptyState text="Nenhum dado disponível." />
    ) : (
      <ol className="space-y-3">
        {items.map((item, index) => (
          <li
            key={item.id}
            className={`flex items-center justify-between gap-3 rounded-lg border p-3 ${rankTone(index)}`}
          >
            <div>
              <p className="font-semibold">
                #{index + 1} {item.full_name || item.username}
              </p>
              <p className="text-sm text-gray-500">@{item.username}</p>
            </div>
            <span className="text-sm font-bold">{metric(item)}</span>
          </li>
        ))}
      </ol>
    )}
  </Card>
);

const CommunityPage = () => {
  const { isAuthenticated } = useAuthContext();
  const [retentionBoard, setRetentionBoard] = useState<PublicUserStats[]>([]);
  const [streakBoard, setStreakBoard] = useState<PublicUserStats[]>([]);
  const [activeBoard, setActiveBoard] = useState<PublicUserStats[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [boardError, setBoardError] = useState<string | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBoards = async () => {
      setLoading(true);
      setBoardError(null);
      try {
        const [retention, streak, active] = await Promise.all([
          getLeaderboardByRetention(),
          getLeaderboardByStreak(),
          getLeaderboardByActive(),
        ]);
        setRetentionBoard(retention);
        setStreakBoard(streak);
        setActiveBoard(active);
      } catch (error) {
        setBoardError(getApiErrorMessage(error, 'Erro ao carregar leaderboard.'));
      } finally {
        setLoading(false);
      }
    };

    void fetchBoards();
  }, []);

  const handleSearch = async (event: React.FormEvent) => {
    event.preventDefault();

    setSearchError(null);
    setSearchResults([]);

    if (!isAuthenticated || !searchTerm.trim()) {
      if (!isAuthenticated) {
        setSearchError('Faça login para pesquisar usuários.');
      }
      return;
    }

    setSearching(true);
    try {
      setSearchResults(await searchUsers(searchTerm.trim()));
    } catch (error) {
      setSearchResults([]);
      setSearchError(getApiErrorMessage(error, 'Erro ao buscar usuários.'));
    } finally {
      setSearching(false);
    }
  };

  return (
    <PageContainer className="max-w-6xl mt-2 space-y-6">
      <div>
        <h1 className="mb-2 text-3xl font-bold">Comunidade</h1>
        <p className="text-gray-600">
          O leaderboard é público. A busca por usuários exige autenticação.
        </p>
      </div>

      {loading ? (
        <Card>
          <p>Carregando leaderboard...</p>
        </Card>
      ) : boardError ? (
        <Alert variant="error">{boardError}</Alert>
      ) : (
        <div className="grid gap-6 xl:grid-cols-3">
          <LeaderboardCard
            title="Top retenção"
            items={retentionBoard}
            metric={item => `${item.best_retention_time}s`}
          />
          <LeaderboardCard
            title="Top streak"
            items={streakBoard}
            metric={item => `${item.current_streak} dias`}
          />
          <LeaderboardCard
            title="Mais ativos"
            items={activeBoard}
            metric={item => `${item.total_sessions} sessões`}
          />
        </div>
      )}

      <Card compact>
        <div className="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <h2 className="text-xl font-semibold">Buscar usuários</h2>
          {!isAuthenticated && (
            <span className="text-sm text-gray-500">
              Faça login para pesquisar outros usuários.
            </span>
          )}
        </div>

        <form onSubmit={handleSearch} className="flex flex-col gap-3 md:flex-row">
          <label className="ui-field flex-1">
            <span className="sr-only">Buscar por username</span>
            <input
              type="text"
              value={searchTerm}
              onChange={event => setSearchTerm(event.target.value)}
              disabled={!isAuthenticated}
              placeholder="Buscar por username"
              className="ui-field__control disabled:bg-gray-100"
            />
          </label>
          <Button type="submit" disabled={!isAuthenticated || searching}>
            {searching ? 'Buscando...' : 'Buscar'}
          </Button>
        </form>

        {searchError && (
          <div className="mt-4">
            <Alert variant="error">{searchError}</Alert>
          </div>
        )}

        {searchResults.length > 0 && (
          <ul className="mt-4 grid gap-3 md:grid-cols-2">
            {searchResults.map(result => (
              <li key={result.id} className="rounded border p-3">
                <p className="font-semibold">{result.full_name || result.username}</p>
                <p className="text-sm text-gray-500">@{result.username}</p>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </PageContainer>
  );
};

export default CommunityPage;
