import { useEffect, useMemo, useState } from 'react';
import AchievementItem from './AchievementItem';
import { useAchievement } from './useAchievement';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Alert from '../../components/ui/Alert';
import PageContainer from '../../components/ui/PageContainer';
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

type SummaryCardProps = {
  label: string;
  value: string | number;
};

const SummaryCard = ({ label, value }: SummaryCardProps) => (
  <Card compact>
    <p className="text-sm text-gray-500">{label}</p>
    <p className="text-xl font-bold">{value}</p>
  </Card>
);

const EmptyState = ({ text }: { text: string }) => <p className="text-gray-600">{text}</p>;

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
    void fetchMyAchievements();
  }, [fetchMyAchievements]);

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
    <PageContainer className="max-w-6xl mt-2">
      <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <h1 className="text-2xl font-bold">Conquistas</h1>
        <Button type="button" onClick={handleCheckAchievements} disabled={checking}>
          {checking ? 'Verificando...' : 'Verificar novas conquistas'}
        </Button>
      </div>

      <section className="mb-6 grid grid-cols-1 gap-3 md:grid-cols-3">
        <SummaryCard label="Pontos" value={totalPoints} />
        <SummaryCard label="Desbloqueadas" value={filteredUnlocked.length} />
        <SummaryCard label="Conclusão" value={`${completion}%`} />
      </section>

      <Card className="mb-6">
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <label className="ui-field">
            <span className="ui-field__label">Categoria</span>
            <select
              value={category}
              onChange={event =>
                setCategory(event.target.value as AchievementCategory | 'all')
              }
              className="ui-field__control"
            >
              {categoryOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="ui-field">
            <span className="ui-field__label">Raridade</span>
            <select
              value={rarity}
              onChange={event =>
                setRarity(event.target.value as AchievementRarity | 'all')
              }
              className="ui-field__control"
            >
              {rarityOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </Card>

      {loading ? (
        <Card>
          <p>Carregando conquistas...</p>
        </Card>
      ) : error ? (
        <Alert variant="error">{error}</Alert>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
          <div>
            <h2 className="mb-3 text-xl font-semibold">Desbloqueadas</h2>
            {filteredUnlocked.length === 0 ? (
              <div className="mb-8">
                <EmptyState text="Nenhuma conquista desbloqueada com os filtros atuais." />
              </div>
            ) : (
              <ul className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-2">
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

            <h2 className="mb-3 text-xl font-semibold">Em progresso</h2>
            {filteredLocked.length === 0 ? (
              <EmptyState text="Nenhuma conquista em progresso com os filtros atuais." />
            ) : (
              <ul className="grid grid-cols-1 gap-4 md:grid-cols-2">
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

          <Card className="h-fit lg:sticky lg:top-6" compact>
            <h2 className="mb-3 text-lg font-bold">Detalhe da conquista</h2>
            {detailLoading ? (
              <p className="text-gray-600">Carregando detalhe...</p>
            ) : selectedAchievement ? (
              <div className="space-y-3">
                <div>
                  <p className="text-2xl font-bold">
                    {selectedAchievement.icon} {selectedAchievement.name}
                  </p>
                  <p className="mt-1 text-sm text-gray-600">
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
                  <Alert variant="success">
                    Desbloqueada em{' '}
                    {selectedAchievement.unlocked_at
                      ? new Date(selectedAchievement.unlocked_at).toLocaleString('pt-BR')
                      : 'data indisponível'}
                    .
                  </Alert>
                ) : selectedAchievement.progress ? (
                  <Alert variant="info">
                    Progresso: {selectedAchievement.progress.current}/
                    {selectedAchievement.progress.target} (
                    {Math.round(selectedAchievement.progress.percentage)}%)
                  </Alert>
                ) : null}

                <Button type="button" variant="ghost" onClick={clearSelectedAchievement}>
                  Fechar detalhe
                </Button>
              </div>
            ) : (
              <p className="text-sm text-gray-600">
                Clique em uma conquista para ver o detalhe completo.
              </p>
            )}
          </Card>
        </div>
      )}
    </PageContainer>
  );
};

export default AchievementList;
