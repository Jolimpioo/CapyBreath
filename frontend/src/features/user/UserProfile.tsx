import { useEffect, useState } from 'react';
import { useAuthContext } from '../auth/AuthProvider';
import { getMyFullProfile } from '../../api/userApi';
import type { UserProfile as UserProfileData } from '../../types/user.types';
import { getApiErrorMessage } from '../../api/apiError';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Alert from '../../components/ui/Alert';

type ProfileStatProps = {
  label: string;
  value: string | number;
};

const ProfileStat = ({ label, value }: ProfileStatProps) => (
  <div className="rounded-lg border p-4">
    <p className="text-sm text-gray-500">{label}</p>
    <p className="text-2xl font-bold">{value}</p>
  </div>
);

const UserProfile = () => {
  const { user, logout } = useAuthContext();
  const [profile, setProfile] = useState<UserProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;

    const fetchProfile = async () => {
      setLoading(true);
      setError(null);
      try {
        setProfile(await getMyFullProfile());
      } catch (error) {
        setError(getApiErrorMessage(error, 'Erro ao carregar perfil completo.'));
      } finally {
        setLoading(false);
      }
    };

    void fetchProfile();
  }, [user]);

  if (!user) {
    return (
      <Card>
        <p>Usuário não autenticado.</p>
      </Card>
    );
  }

  return (
    <Card className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div className="space-y-2">
          <h1 className="text-2xl font-bold">Perfil</h1>
          <p>
            <strong>Nome:</strong> {user.full_name || 'Não informado'}
          </p>
          <p>
            <strong>Usuário:</strong> @{user.username}
          </p>
          <p>
            <strong>E-mail:</strong> {user.email}
          </p>
          <p>
            <strong>ID:</strong> {user.id}
          </p>
        </div>
        <Button
          type="button"
          variant="danger"
          onClick={() => {
            void logout();
          }}
        >
          Sair
        </Button>
      </div>

      {loading ? (
        <p>Carregando estatísticas do perfil...</p>
      ) : error ? (
        <Alert variant="error">{error}</Alert>
      ) : profile ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <ProfileStat label="Sessões totais" value={profile.total_sessions} />
          <ProfileStat label="Melhor retenção" value={`${profile.best_retention_time}s`} />
          <ProfileStat label="Streak atual" value={profile.current_streak} />
          <ProfileStat
            label="Última sessão"
            value={
              profile.last_session_date
                ? new Date(profile.last_session_date).toLocaleString('pt-BR')
                : 'Sem sessões'
            }
          />
        </div>
      ) : null}
    </Card>
  );
};

export default UserProfile;
