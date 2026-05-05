import Card from '../../components/ui/Card';
import type { SessionDetail } from '../../types/session.types';

interface SessionDetailsProps {
  session?: SessionDetail | null;
}

type DetailMetricProps = {
  label: string;
  value: string | number;
};

const DetailMetric = ({ label, value }: DetailMetricProps) => (
  <div className="rounded-lg border p-4">
    <p className="text-sm text-gray-500">{label}</p>
    <p className="text-lg font-semibold">{value}</p>
  </div>
);

const SessionDetails = ({ session }: SessionDetailsProps) => {
  if (!session) {
    return (
      <Card className="mx-auto max-w-2xl">
        <p>Selecione uma sessão para ver os detalhes.</p>
      </Card>
    );
  }

  const moodImprovement =
    session.mood_before !== null && session.mood_after !== null
      ? session.mood_after - session.mood_before
      : null;

  return (
    <Card className="mx-auto max-w-2xl">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold">Detalhes da sessão</h2>
          <p className="text-sm text-gray-500">
            {new Date(session.session_date).toLocaleString('pt-BR')}
          </p>
        </div>
        {session.is_personal_best && (
          <span className="rounded-full border border-amber-300 bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
            🏆 Personal Best
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <DetailMetric label="Técnica" value={session.technique_variant} />
        <DetailMetric label="Respirações" value={session.breaths_count} />
        <DetailMetric label="Retenção" value={`${session.retention_time}s`} />
        <DetailMetric label="Recuperação" value={`${session.recovery_time}s`} />
        <DetailMetric label="Duração total" value={`${session.duration_seconds}s`} />
        <DetailMetric
          label="Evolução do humor"
          value={
            moodImprovement === null
              ? 'Não informado'
              : `${moodImprovement > 0 ? '+' : ''}${moodImprovement}`
          }
        />
      </div>

      <div className="mt-4 rounded-lg border p-4">
        <p className="text-sm text-gray-500">Notas</p>
        <p className="mt-1 text-gray-800">
          {session.notes?.trim() || 'Nenhuma anotação registrada.'}
        </p>
      </div>
    </Card>
  );
};

export default SessionDetails;
