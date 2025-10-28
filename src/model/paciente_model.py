from model.database import get_connection


class PacienteModel:  # nome é obrigatório, especialidade é recomendado cpf pode ser none e status começa em aguardando
    @staticmethod
    def create(
        nome: str,
        especialidade_req_id: int | None = None,
        cpf: str | None = None,
        telefone: str | None = None,
        data_nascimento: str | None = None,  # y-m-d
        tipo_sanguineo: str | None = None,
        leito: str | None = None,
    ) -> dict:
        if not nome or not nome.strip():
            return {"ok": False, "msg": "Nome do paciente é obrigatório!"}

        # A especialidade não é obrigatória, mas é recomendado ter
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            if especialidade_req_id is not None:
                cur.execute(
                    "SELECT 1 FROM tb_especialidades WHERE id=%s",
                    (especialidade_req_id,),
                )
                if not cur.fetchone():
                    return {"ok": False, "msg": "Especialidade requisitada é inválida!"}

            sql = """
                INSERT INTO tb_pacientes
                (nome, cpf, telefone, data_nascimento, tipo_sanguineo,
                especialidade_req_id, leito, status_ps)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'AGURADANDO')
            """
            cur.execute(
                sql,
                (
                    nome,
                    cpf,
                    telefone,
                    data_nascimento,
                    tipo_sanguineo,
                    especialidade_req_id,
                    leito,
                ),
            )
            conn.commit()
            return {
                "ok": True,
                "msg": "Paciente criado com sucesso!",
                "paciente_id": cur.lastrowid,
            }
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def get_by_id(paciente_id: int) -> dict | None:
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT p.*
                FROM tb_pacientes p
                WHERE p.id=%s
            """,
                (paciente_id,),
            )
            return cur.fetchone()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
