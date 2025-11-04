from model.database import get_connection


class AcoesModel:
    @staticmethod
    def dar_alta(paciente_id: int, medico_cpf: str) -> dict:
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Valida o médico
            cur.execute(
                """
                SELECT 1 FROM tb_funcionarios_hospital
                WHERE cpf=%s AND funcao='MEDICO'
            """,
                (medico_cpf,),
            )
            if not cur.fetchone():
                return {"ok": False, "msg": "Apenas algum médico pode dar alta."}

            # Aplica a alta para o paciente
            cur.execute(
                """
                UPDATE tb_pacientes
                SET status_ps='ALTA'
                WHERE id=%s
            """,
                (paciente_id,),
            )

            # Fecha todos os atendimentos que estão em aberto após a alta
            cur.execute(
                """
                UPDATE tb_atendimentos
                SET status='FECHADO', finalizado_em=CURRENT_TIMESTAMP
                WHERE paciente_id=%s AND status='ABERTO'
            """,
                (paciente_id,),
            )

            conn.commit()
            return {"ok": True, "msg": "Foi dado a alta e o atendimento foi encerrado."}
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def internar(paciente_id: int, medico_cpf: str, motivo: str | None = None) -> dict:
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                """
                SELECT 1 FROM tb_funcionarios_hospital
                WHERE cpf=%s AND funcao='MEDICO'
            """,
                (medico_cpf,),
            )
            if not cur.fetchone():
                return {"ok": False, "msg": "Apenas médico pode internar."}

            cur.execute(  # Interna de maneira única
                "SELECT 1 FROM tb_internacoes WHERE paciente_id=%s", (paciente_id,)
            )
            if cur.fetchone():
                return {"ok": False, "msg": "Paciente já está internado."}

            cur.execute(
                """
                INSERT INTO tb_internacoes (paciente_id, medico_cpf, motivo)
                VALUES (%s,%s,%s)
            """,
                (paciente_id, medico_cpf, motivo),
            )

            cur.execute(  # Define o status e zera o leito do PS
                """
                UPDATE tb_pacientes
                SET status_ps='INTERNADO', leito=NULL
                WHERE id=%s
            """,
                (paciente_id,),
            )

            conn.commit()
            return {"ok": True, "msg": "Paciente internado; dados congelados no PS."}
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
