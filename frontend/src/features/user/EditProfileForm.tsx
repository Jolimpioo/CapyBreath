import { useState } from 'react';
import { updateProfile } from '../../api/userApi';
import { useAuthContext } from '../auth/AuthProvider';
import { getApiErrorMessage } from '../../api/apiError';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Alert from '../../components/ui/Alert';
import InputField from '../../components/ui/InputField';

const EditProfileForm = () => {
  const { user, setUser, showToast } = useAuthContext();
  const [fullName, setFullName] = useState(user?.full_name ?? '');
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url ?? '');
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!user) {
    return (
      <Card>
        <p>Usuário não autenticado.</p>
      </Card>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const updated = await updateProfile({
        full_name: fullName.trim() ? fullName.trim() : null,
        avatar_url: avatarUrl.trim() ? avatarUrl.trim() : null,
      });
      setUser(updated);
      setSuccess('Perfil atualizado com sucesso!');
      showToast('Perfil atualizado com sucesso!', 'success');
    } catch (error) {
      const message = getApiErrorMessage(error, 'Erro ao atualizar perfil.');
      setError(message);
      showToast(message, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <header>
          <h2 className="text-2xl font-bold">Editar Perfil</h2>
          <p className="mt-1 text-sm text-gray-600">
            Atualize seus dados visíveis e informações de avatar.
          </p>
        </header>

        {success && <Alert variant="success">{success}</Alert>}
        {error && <Alert variant="error">{error}</Alert>}

        <InputField
          label="Nome completo"
          type="text"
          placeholder="Nome completo"
          value={fullName}
          onChange={e => setFullName(e.target.value)}
        />
        <InputField
          label="URL do avatar"
          type="url"
          placeholder="https://exemplo.com/avatar.png"
          value={avatarUrl}
          onChange={e => setAvatarUrl(e.target.value)}
        />

        <Button type="submit" disabled={loading}>
          {loading ? 'Salvando...' : 'Salvar alterações'}
        </Button>
      </form>
    </Card>
  );
};

export default EditProfileForm;
