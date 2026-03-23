import { useEffect, useMemo, useState } from 'react';
import AchievementItem from './AchievementItem';
import { useAchievement } from './useAchievement';
import type {
  AchievementCategory,
  AchievementRarity,
  LockedAchievement,
  UnlockedAchievement,
} from '../../types/achievement.types';

const categoryOptions: Array<{ value: AchievementCategory | 'all'; label: string }> = [
  { value: 'all', label: 'Todas categorias' },
  { value: 'sessions', label: 'Sessões' },
  { value: 'retention', label: 'Retenção' },
  { value: 'streak', label: 'Streak' },
  { value: 'improvement', label: 'Evolução' },
  { value: 'milestone', label: 'Marcos' },
];

const rarityOptions: Array<{ value: AchievementRarity | 'all'; label: string }> = [
  { value: 'all', label: 'Todas raridades' },
  { value: 'common', label: 'Common' },
  { value: 'rare', label: 'Rare' },
  { value: 'epic', label: 'Epic' },
  { value: 'legendary', label: 'Legendary' },
];

const AchievementList = () => {
  const {
    catalog,
    userAchievements,
    selectedAchievement,
    loading,
    detailLoading,
    error,
    fetchCatalog,
    fetchMyAchievements,
    fetchAchievementDetail,
    clearSelectedAchievement,
    checkAndUnlock,
  } = useAchievement();
  const [checking, setChecking] = useState(false);
  const [category, setCategory] = useState<AchievementCategory | 'all'>('all');
  const [rarity, setRarity] = useState<AchievementRarity | 'all'>('all');

  useEffect(() => {
    void Promise.all([
      fetchCatalog({ category: 'all', rarity: 'all' }),
      fetchMyAchievements(),
    ]);
  }, [fetchCatalog, fetchMyAchievements]);

  useEffect(() => {
    void fetchCatalog({ category, rarity });
  }, [category, rarity, fetchCatalog]);

  const totalPoints = userAchievements?.total_points ?? 0;

  const allowedIds = useMemo(() => new Set(catalog.map(item => item.id)), [catalog]);

  const filteredUnlocked = useMemo(() => {
    const unlocked = userAchievements?.unlocked ?? [];
    return unlocked.filter(item => allowedIds.has(item.id));
  }, [allowedIds, userAchievements]);

  const filteredLocked = useMemo(() => {
    const locked = userAchievements?.locked ?? [];
    return locked.filter(item => allowedIds.has(item.id));
  }, [allowedIds, userAchievements]);

  const completion = useMemo(() => {
    const total = filteredUnlocked.length + filteredLocked.length;
    if (!total) return 0;
    return Math.round((filteredUnlocked.length / total) * 100);
  }, [filteredLocked.length, filteredUnlocked.length]);

  const handleCheckAchievements = async () => {
    setChecking(true);
    try {
      await checkAndUnlock();
      await Promise.all([
        fetchCatalog({ category, rarity }),
        fetchMyAchievements(),
      ]);
    } finally {
      setChecking(false);
    }
  };

  const handleSelectAchievement = async (
    achievement: LockedAchievement | UnlockedAchievement
  ) => {
    await fetchAchievementDetail(achievement.id);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 mt-8">
      <div className="flex flex-col gap-2 mb-6 md:flex-row md:items-center md:justify-between">
        <h1 className="text-2xl font-bold">Conquistas</h1>
        <button
          type="button"
          onClick={handleCheckAchievements}
          disabled={checking}
          className="bg-capy-primary text-white px-4 py-2 rounded hover:bg-capy-primary/90 disabled:opacity-50"
        >
          {checking ? 'Verificando...' : 'Verificar novas conquistas'}
        </button>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-3 md:grid-cols-3">
        <div className="bg-white rounded-lg border p-4">
          <p className="text-sm text-gray-500">Pontos</p>
          <p className="text-xl font-bold">{totalPoints}</p>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <p className="text-sm text-gray-500">Desbloqueadas</p>
          <p className="text-xl font-bold">{filteredUnlocked.length}</p>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <p className="text-sm text-gray-500">Conclusão</p>
          <p className="text-xl font-bold">{completion}%</p>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-3 md:grid-cols-2">
        <label className="block">
          <span className="mb-1 block text-sm font-medium text-gray-700">
            Categoria
          </span>
          <select
            value={category}
            onChange={event =>
              setCategory(event.target.value as AchievementCategory | 'all')
            }
            className="w-full rounded border px-3 py-2"
          >
            {categoryOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium text-gray-700">
            Raridade
          </span>
          <select
            value={rarity}
            onChange={event =>
              setRarity(event.target.value as AchievementRarity | 'all')
            }
            className="w-full rounded border px-3 py-2"
          >
            {rarityOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading ? (
        <div>Carregando conquistas...</div>
      ) : error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
          <div>
            <h2 className="text-xl font-semibold mb-3">Desbloqueadas</h2>
            {filteredUnlocked.length === 0 ? (
              <div className="mb-8 text-gray-600">
                Nenhuma conquista desbloqueada com os filtros atuais.
              </div>
            ) : (
              <ul className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredUnlocked.map(achievement => (
                  <li key={achievement.id}>
                    <AchievementItem
                      achievement={achievement}
                      unlocked
                      onClick={() => void handleSelectAchievement(achievement)}
                    />
                  </li>
                ))}
              </ul>
            )}

            <h2 className="text-xl font-semibold mb-3">Em progresso</h2>
            {filteredLocked.length === 0 ? (
              <div className="text-gray-600">
                Nenhuma conquista em progresso com os filtros atuais.
              </div>
            ) : (
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredLocked.map(achievement => (
                  <li key={achievement.id}>
                    <AchievementItem
                      achievement={achievement}
                      onClick={() => void handleSelectAchievement(achievement)}
                    />
                  </li>
                ))}
              </ul>
            )}
          </div>

          <aside className="rounded-xl border bg-white p-5 shadow-sm h-fit lg:sticky lg:top-6">
            <h2 className="text-lg font-bold mb-3">Detalhe da conquista</h2>
            {detailLoading ? (
              <p className="text-gray-600">Carregando detalhe...</p>
            ) : selectedAchievement ? (
              <div className="space-y-3">
                <div>
                  <p className="text-2xl font-bold">
                    {selectedAchievement.icon} {selectedAchievement.name}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {selectedAchievement.description}
                  </p>
                </div>
                <div className="grid gap-2 text-sm">
                  <p>
                    <span className="font-semibold">Categoria:</span>{' '}
                    {selectedAchievement.category}
                  </p>
                  <p>
                    <span className="font-semibold">Raridade:</span>{' '}
                    {selectedAchievement.rarity}
                  </p>
                  <p>
                    <span className="font-semibold">Pontos:</span>{' '}
                    {selectedAchievement.points}
                  </p>
                  <p>
                    <span className="font-semibold">Status:</span>{' '}
                    {selectedAchievement.unlocked ? 'Desbloqueada' : 'Em progresso'}
                  </p>
                </div>

                {selectedAchievement.unlocked ? (
                  <div className="rounded-lg bg-green-50 border border-green-200 p-3 text-sm text-green-800">
                    Desbloqueada em{' '}
                    {selectedAchievement.unlocked_at
                      ? new Date(selectedAchievement.unlocked_at).toLocaleString('pt-BR')
                      : 'data indisponível'}
                    .
                  </div>
                ) : selectedAchievement.progress ? (
                  <div className="rounded-lg bg-gray-50 border p-3 text-sm text-gray-700">
                    Progresso: {selectedAchievement.progress.current}/
                    {selectedAchievement.progress.target} (
                    {Math.round(selectedAchievement.progress.percentage)}%)
                  </div>
                ) : null}

                <button
                  type="button"
                  onClick={clearSelectedAchievement}
                  className="rounded border px-4 py-2 text-sm font-medium hover:bg-gray-50"
                >
                  Fechar detalhe
                </button>
              </div>
            ) : (
              <p className="text-gray-600 text-sm">
                Clique em uma conquista para ver o detalhe completo.
              </p>
            )}
          </aside>
        </div>
      )}
    </div>
  );
};

export default AchievementList;
