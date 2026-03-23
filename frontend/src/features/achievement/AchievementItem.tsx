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
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left transition hover:shadow-sm ${
        unlocked
          ? 'p-4 rounded border-2 border-green-500 bg-green-50'
          : 'p-4 rounded border bg-gray-50'
      }`}
    >
      <p className="font-bold text-lg">
        {achievement.icon} {achievement.name}
      </p>
      <p className="text-sm text-gray-600">{achievement.description}</p>
      {'progress' in achievement ? (
        <p className="text-xs text-gray-500 mt-2">
          Progresso: {achievement.progress.current}/{achievement.progress.target}{' '}
          ({Math.round(achievement.progress.percentage)}%)
        </p>
      ) : (
        <p className="text-xs text-green-700 mt-2">
          +{achievement.points} pts • {achievement.rarity}
        </p>
      )}
    </button>
  );
};

export default AchievementItem;
