import type {
  LockedAchievement,
  UnlockedAchievement,
} from '../../types/achievement.types';

type AchievementItemProps = {
  achievement: LockedAchievement | UnlockedAchievement;
  unlocked?: boolean;
  onClick?: () => void;
};

const AchievementItem = ({
  achievement,
  unlocked = false,
  onClick,
}: AchievementItemProps) => {
  const stateClass = unlocked
    ? 'border-capy-accent bg-green-50 text-green-800'
    : 'border-capy-secondary/35 bg-white text-gray-700';

  return (
    <button
      type="button"
      onClick={onClick}
      className={`min-h-[44px] w-full rounded-lg border p-4 text-left transition hover:shadow-sm focus-visible:border-capy-accent ${stateClass}`}
    >
      <p className="text-lg font-bold">
        {achievement.icon} {achievement.name}
      </p>
      <p className="text-sm text-gray-600">{achievement.description}</p>
      {'progress' in achievement ? (
        <p className="mt-2 text-xs text-gray-500">
          Progresso: {achievement.progress.current}/{achievement.progress.target}{' '}
          ({Math.round(achievement.progress.percentage)}%)
        </p>
      ) : (
        <p className="mt-2 text-xs font-semibold text-green-700">
          +{achievement.points} pts • {achievement.rarity}
        </p>
      )}
    </button>
  );
};

export default AchievementItem;
