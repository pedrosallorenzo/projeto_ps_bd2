from model.database import get_connection


class ProntuarioModel:
    @staticmethod
    def get(paciente_id: int) -> dict | None:
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT pr.*, p.status_ps, p.nome AS paciente_nome
                FROM tb_prontuarios pr
                JOIN tb_pacientes p ON p.id = pr.paciente_id
                WHERE pr.paciente_id = %s
            """,
                (paciente_id,),
            )
            return cur.fetchone()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def get_or_create(paciente_id: int, medico_cpf: str) -> dict:
        pr = ProntuarioModel.get(paciente_id)
        if pr:
            return {"ok": True, "msg": "Prontuário existente.", "prontuario": pr}

        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(  # faz a validação do médico
                """
                SELECT 1 FROM tb_funcionarios_hospital
                WHERE cpf=%s AND funcao='MEDICO'
            """,
                (medico_cpf,),
            )
            if not cur.fetchone():
                return {"ok": False, "msg": "Apenas médico pode abrir prontuário."}

            cur.execute(  # faz a validação do paciente
                "SELECT status_ps FROM tb_pacientes WHERE id=%s", (paciente_id,)
            )
            row = cur.fetchone()
            if not row:
                return {"ok": False, "msg": "Paciente não encontrado."}

            cur.execute(
                """
                INSERT INTO tb_prontuarios (paciente_id, medico_cpf)
                VALUES (%s, %s)
            """,
                (paciente_id, medico_cpf),
            )
            conn.commit()
            return {
                "ok": True,
                "msg": "Prontuário criado.",
                "prontuario_id": cur.lastrowid,
            }
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def salvar(  # atualiza os dados do prontuario do paciente
        paciente_id: int,
        medico_cpf: str,
        *,
        historico_medico: str | None = None,
        sintomas: str | None = None,
        conduta: str | None = None,
        diagnostico: str | None = None,
        observacoes: str | None = None,
    ) -> dict:

        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute(  # permissões e status
                """
                SELECT p.status_ps
                FROM tb_pacientes p
                WHERE p.id=%s
            """,
                (paciente_id,),
            )
            row = cur.fetchone()
            if not row:
                return {"ok": False, "msg": "Paciente não encontrado."}
            (status_ps,) = row
            if status_ps in ("INTERNADO", "ALTA"):
                return {
                    "ok": False,
                    "msg": f"Edição bloqueada: paciente está {status_ps}.",
                }

            cur.execute(
                """
                SELECT 1 FROM tb_funcionarios_hospital
                WHERE cpf=%s AND funcao='MEDICO'
            """,
                (medico_cpf,),
            )
            if not cur.fetchone():
                return {"ok": False, "msg": "Apenas médico pode editar prontuário."}

            cur.execute(  # checa se existe o paciente
                "SELECT 1 FROM tb_prontuarios WHERE paciente_id=%s", (paciente_id,)
            )
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO tb_prontuarios (paciente_id, medico_cpf) VALUES (%s,%s)",
                    (paciente_id, medico_cpf),
                )
            # atualiza os campos que foram alterados
            sql = """
                UPDATE tb_prontuarios
                SET historico_medico=COALESCE(%s, historico_medico),
                    sintomas=COALESCE(%s, sintomas),
                    conduta=COALESCE(%s, conduta),
                    diagnostico=COALESCE(%s, diagnostico),
                    observacoes=COALESCE(%s, observacoes),
                    atualizado_em=CURRENT_TIMESTAMP
                WHERE paciente_id=%s
            """
            cur.execute(
                sql,
                (
                    historico_medico,
                    sintomas,
                    conduta,
                    diagnostico,
                    observacoes,
                    paciente_id,
                ),
            )
            conn.commit()
            return {"ok": True, "msg": "Prontuário salvo."}
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
