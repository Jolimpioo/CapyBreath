import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import SessionDetails from '../features/session/SessionDetails';
import {
  deleteSession,
  getSessionById,
  updateSession,
} from '../api/sessionApi';
import type {
  SessionDetail,
  SessionUpdateRequest,
} from '../types/session.types';
import { getApiErrorMessage } from '../api/apiError';
import { useAuthContext } from '../features/auth/AuthProvider';
import PageContainer from '../components/ui/PageContainer';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Alert from '../components/ui/Alert';
import InputField from '../components/ui/InputField';

const moodOptions = Array.from({ length: 10 }, (_, index) => index + 1);

const SessionDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showToast } = useAuthContext();
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [notes, setNotes] = useState('');
  const [moodBefore, setMoodBefore] = useState('');
  const [moodAfter, setMoodAfter] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setError('Sessão inválida.');
      setLoading(false);
      return;
    }

    const fetchSession = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getSessionById(id);
        setSession(data);
        setNotes(data.notes ?? '');
        setMoodBefore(data.mood_before?.toString() ?? '');
        setMoodAfter(data.mood_after?.toString() ?? '');
      } catch (error) {
        setError(getApiErrorMessage(error, 'Erro ao carregar sessão.'));
      } finally {
        setLoading(false);
      }
    };

    void fetchSession();
  }, [id]);

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!id) return;

    setSaving(true);
    setError(null);
    setSuccessMessage(null);

    const payload: SessionUpdateRequest = {
      notes: notes.trim() ? notes.trim() : null,
      mood_before: moodBefore ? Number(moodBefore) : null,
      mood_after: moodAfter ? Number(moodAfter) : null,
    };

    try {
      const updated = await updateSession(id, payload);
      setSession(prev =>
        prev
          ? {
              ...prev,
              ...updated,
              is_personal_best: prev.is_personal_best,
            }
          : null
      );
      setSuccessMessage('Sessão atualizada com sucesso.');
      showToast('Sessão atualizada com sucesso!', 'success');
    } catch (error) {
      const message = getApiErrorMessage(error, 'Erro ao atualizar sessão.');
      setError(message);
      showToast(message, 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!id || !session) return;

    const confirmed = window.confirm(
      'Tem certeza que deseja excluir esta sessão do seu histórico?'
    );

    if (!confirmed) return;

    setDeleting(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await deleteSession(id);
      showToast('Sessão excluída com sucesso.', 'success');
      navigate('/session');
    } catch (error) {
      const message = getApiErrorMessage(error, 'Erro ao excluir sessão.');
      setError(message);
      showToast(message, 'error');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <PageContainer className="max-w-4xl mt-2">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <p className="text-sm">Histórico de Sessões</p>
          <h1 className="text-2xl font-bold">Detalhe da sessão</h1>
        </div>
        <Link to="/session">
          <Button variant="ghost" type="button">
            ← Voltar ao histórico
          </Button>
        </Link>
      </div>

      {loading ? (
        <Card>
          <p>Carregando sessão...</p>
        </Card>
      ) : error && !session ? (
        <Alert variant="error">{error}</Alert>
      ) : (
        <>
          <SessionDetails session={session} />

          <Card className="mx-auto mt-6 max-w-2xl">
            <form onSubmit={handleSave} className="space-y-4">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <h2 className="text-xl font-bold">Editar sessão</h2>
                <Button
                  type="button"
                  onClick={handleDelete}
                  disabled={deleting}
                  variant="danger"
                >
                  {deleting ? 'Excluindo...' : 'Excluir sessão'}
                </Button>
              </div>

              {error && session && <Alert variant="error">{error}</Alert>}
              {successMessage && (
                <Alert variant="success">{successMessage}</Alert>
              )}

              <InputField
                label="Notas"
                multiline
                rows={4}
                maxLength={500}
                value={notes}
                onChange={event => setNotes(event.target.value)}
                placeholder="Adicione observações sobre esta prática"
              />

              <div className="grid gap-4 md:grid-cols-2">
                <label className="ui-field">
                  <span className="ui-field__label">Humor antes</span>
                  <select
                    value={moodBefore}
                    onChange={event => setMoodBefore(event.target.value)}
                    className="ui-field__control"
                  >
                    <option value="">Não informado</option>
                    {moodOptions.map(option => (
                      <option key={`before-${option}`} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="ui-field">
                  <span className="ui-field__label">Humor depois</span>
                  <select
                    value={moodAfter}
                    onChange={event => setMoodAfter(event.target.value)}
                    className="ui-field__control"
                  >
                    <option value="">Não informado</option>
                    {moodOptions.map(option => (
                      <option key={`after-${option}`} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="flex justify-end">
                <Button type="submit" disabled={saving || deleting}>
                  {saving ? 'Salvando...' : 'Salvar alterações'}
                </Button>
              </div>
            </form>
          </Card>
        </>
      )}
    </PageContainer>
  );
};

export default SessionDetailPage;
