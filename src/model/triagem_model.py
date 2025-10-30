# Registra a triagem
# Aplica as regras de prioridade e sintomas
# O funcionário operante tem que ser o técnico de enfermagem

from model.database import get_connection


class TriagemModel:
    @staticmethod
    def create(
        paciente_id: int,
        tecnico_cpf: str,
        sintomas: str,
        prioridade: str,
        pa: str | None = None,
        pulso: int | None = None,
        saturacao: int | None = None,
        temperatura_c: float | None = None,
        historico_medico: str | None = None,
    ) -> dict:
        if not sintomas or not prioridade:
            return {"ok": False, "msg": "Campos obrigatórios: sintomas e prioridade."}

        if prioridade not in ("LEVE", "MODERADA", "ALTA"):
            return {"ok": False, "msg": "Prioridade inválida!"}

        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "SELECT 1 FROM tb_pacientes WHERE id=%s", (paciente_id,)
            )  # Verifica se o paciente já está cadastrado (secretaria do hospital)
            if not cur.fetchone():
                return {"ok": False, "msg": "Paciente não encontrado."}

            cur.execute(
                "SELECT 1 FROM tb_funcionarios_hospital WHERE cpf=%s AND funcao='TECNICO_DE_ENFERMAGEM'",
                (tecnico_cpf,),
            )
            if not cur.fetchone():
                return {"ok": False, "msg": "Técnico de enfermagem inválido."}

            cur.execute(  # Executa o comando para criar a triagem
                "INSERT INTO tb_triagens "
                "(paciente_id, tecnico_cpf, pa, pulso, saturacao, temperatura_c, historico_medico, sintomas, prioridade)"
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    paciente_id,
                    tecnico_cpf,
                    pa,
                    pulso,
                    saturacao,
                    temperatura_c,
                    historico_medico,
                    sintomas,
                    prioridade,
                ),
            )
            conn.commit()
            return {
                "ok": True,
                "msg": "Triagem registrada com sucesso!",
                "triagem_id": cur.lastrowid,
            }
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
