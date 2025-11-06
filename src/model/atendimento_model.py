# Limita a visão do médico e do enfermeiro,
# fazendo com que somente os pacientes que ainda
# necessitam de atendimento, aparecam para eles

from .database import get_connection


class AtendimentoModel:
    @staticmethod  # Abre o atendimento
    def abrir(paciente_id: int, funcionario_cpf: str, funcao: str) -> dict:
        if funcao not in ("MEDICO", "ENFERMEIRO"):
            return {"ok": False, "msg": "Função inválida."}

        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute(  # valida funcionário/função
                """
                SELECT 1 FROM tb_funcionarios_hospital
                WHERE cpf=%s AND funcao=%s
            """,
                (funcionario_cpf, funcao),
            )
            if not cur.fetchone():
                return {"ok": False, "msg": "Funcionário/função inválido(s)."}

            cur.execute(  # checa lock por função
                """
                SELECT 1 FROM tb_atendimentos
                WHERE paciente_id=%s AND funcao=%s AND status='ABERTO'
            """,
                (paciente_id, funcao),
            )
            if cur.fetchone():
                return {
                    "ok": False,
                    "msg": "Paciente já está em atendimento para essa função.",
                }

            cur.execute(  # abre
                """ 
                INSERT INTO tb_atendimentos (paciente_id, funcionario_cpf, funcao, status)
                VALUES (%s,%s,%s,'ABERTO')
            """,
                (paciente_id, funcionario_cpf, funcao),
            )

            # marca paciente como "EM_ATENDIMENTO"
            cur.execute(
                """
                UPDATE tb_pacientes SET status_ps='EM_ATENDIMENTO'
                WHERE id=%s
            """,
                (paciente_id,),
            )
            conn.commit()
            return {"ok": True, "msg": "Atendimento aberto."}
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    class AtendimentoModel:
        @staticmethod  # Fecha o atendimento
        def fechar(paciente_id: int, funcionario_cpf: str) -> dict:
            conn = cur = None
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                UPDATE tb_atendimentos
                SET status='FECHADO', finalizado_em=CURRENT_TIMESTAMP
                WHERE paciente_id=%s AND funcionario_cpf=%s AND status='ABERTO'
            """,
                    (paciente_id, funcionario_cpf),
                )
                conn.commit()
                if cur.rowcount == 0:
                    return {
                        "ok": False,
                        "msg": "Nenhum atendimento está aberto no momento.",
                    }
                return {"ok": True, "msg": "Atendimento fechado."}
            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()
