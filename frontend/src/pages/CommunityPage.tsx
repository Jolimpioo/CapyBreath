import { useEffect, useState } from 'react';
import { getApiErrorMessage } from '../api/apiError';
import {
  getLeaderboardByActive,
  getLeaderboardByRetention,
  getLeaderboardByStreak,
  searchUsers,
} from '../api/userApi';
import type { User, UserStats } from '../types/user.types';
import { useAuthContext } from '../features/auth/AuthProvider';

const CommunityPage = () => {
  const { isAuthenticated } = useAuthContext();
  const [retentionBoard, setRetentionBoard] = useState<UserStats[]>([]);
  const [streakBoard, setStreakBoard] = useState<UserStats[]>([]);
  const [activeBoard, setActiveBoard] = useState<UserStats[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBoards = async () => {
      setLoading(true);
      setError(null);
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
        setError(getApiErrorMessage(error, 'Erro ao carregar leaderboard.'));
      } finally {
        setLoading(false);
      }
    };

    void fetchBoards();
  }, []);

  const handleSearch = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!isAuthenticated || !searchTerm.trim()) {
      setSearchResults([]);
      return;
    }

    setSearching(true);
    try {
      setSearchResults(await searchUsers(searchTerm.trim()));
    } catch (error) {
      setError(getApiErrorMessage(error, 'Erro ao buscar usuários.'));
    } finally {
      setSearching(false);
    }
  };

  const renderBoard = (
    title: string,
    items: UserStats[],
    metric: (item: UserStats) => string
  ) => (
    <section className="rounded-xl border bg-white p-5 shadow-sm">
      <h2 className="text-xl font-semibold mb-3">{title}</h2>
      {items.length === 0 ? (
        <p className="text-gray-600">Nenhum dado disponível.</p>
      ) : (
        <ol className="space-y-3">
          {items.map((item, index) => (
            <li key={item.id} className="flex items-center justify-between rounded border p-3">
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
    </section>
  );

  return (
    <div className="max-w-6xl mx-auto p-6 mt-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Comunidade</h1>
        <p className="text-gray-600">
          O leaderboard é visível para todos. A busca por usuários fica disponível apenas para usuários autenticados.
        </p>
      </div>

      {loading ? (
        <div>Carregando leaderboard...</div>
      ) : error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      ) : (
        <div className="grid gap-6 xl:grid-cols-3">
          {renderBoard('Top retenção', retentionBoard, item => `${item.best_retention_time}s`)}
          {renderBoard('Top streak', streakBoard, item => `${item.current_streak} dias`)}
          {renderBoard('Mais ativos', activeBoard, item => `${item.total_sessions} sessões`)}
        </div>
      )}

      <section className="rounded-xl border bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between gap-3 mb-4">
          <h2 className="text-xl font-semibold">Buscar usuários</h2>
          {!isAuthenticated && (
            <span className="text-sm text-gray-500">
              Faça login para pesquisar outros usuários.
            </span>
          )}
        </div>

        <form onSubmit={handleSearch} className="flex flex-col gap-3 md:flex-row">
          <input
            type="text"
            value={searchTerm}
            onChange={event => setSearchTerm(event.target.value)}
            disabled={!isAuthenticated}
            placeholder="Buscar por username"
            className="flex-1 rounded border px-3 py-2 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={!isAuthenticated || searching}
            className="rounded bg-capy-primary px-4 py-2 font-semibold text-white hover:bg-capy-primary/90 disabled:opacity-50"
          >
            {searching ? 'Buscando...' : 'Buscar'}
          </button>
        </form>

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
      </section>
    </div>
  );
};

export default CommunityPage;
