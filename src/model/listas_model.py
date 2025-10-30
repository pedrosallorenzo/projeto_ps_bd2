# Cria a lista para os médicos e enfermeiros
# p/ os médicos, ela é filtrada
# p/ os enfermeiros, eles veem todos, MENOS os que já foram dado alta

from model.database import get_connection


class ListasModel:
    @staticmethod
    def pacientes_para_medico(medico_cpf: str) -> list[dict]:
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)

            cur.execute(  # Seleciona a especialidade do médico
                "SELECT especialidade_id FROM tb_funcionarios_hospital WHERE cpf=%s AND funcao='MEDICO'",
                (medico_cpf,),
            )
            row = cur.fetchone()
            if not row or row["especialidade_id"] is None:
                return []

            esp_id = row["especialidade_id"]

            cur.execute(  # Pacientes da especialidade fora de atendimento por outro médico
                """
                SELECT p.id, p.nome, 
                       TIMESTAMPDIFF(YEAR, p.data_nascimento, CURDATE()) AS idade,
                       e.nome AS especialidade, 
                       p.status_ps,
                       t.prioridade
                FROM tb_pacientes p
                LEFT JOIN tb_especialidades e ON e.id = p.especialidade_req_id
                LEFT JOIN tb_triagens t ON t.paciente_id = p.id
                WHERE p.especialidade_req_id = %s
                  AND p.status_ps <> 'ALTA'
                  AND NOT EXISTS (
                    SELECT 1
                    FROM tb_atendimentos a
                    JOIN tb_funcionarios_hospital f ON f.cpf = a.funcionario_cpf
                    WHERE a.paciente_id = p.id
                      AND a.status = 'ABERTO'
                      AND f.funcao = 'MEDICO'
                      AND a.funcionario_cpf <> %s
                  )
                ORDER BY p.atualizado_em DESC, p.id DESC
            """,
                (esp_id, medico_cpf),
            )
            return cur.fetchall()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def pacientes_para_enfermeiro() -> list[dict]:
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT p.id, p.nome, 
                       TIMESTAMPDIFF(YEAR, p.data_nascimento, CURDATE()) AS idade,
                       e.nome AS especialidade, 
                       p.status_ps,
                       t.prioridade
                FROM tb_pacientes p
                LEFT JOIN tb_especialidades e ON e.id = p.especialidade_req_id
                LEFT JOIN tb_triagens t ON t.paciente_id = p.id
                WHERE p.status_ps <> 'ALTA'
                ORDER BY p.atualizado_em DESC, p.id DESC
            """
            )
            return cur.fetchall()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def meus_atendimentos_abertos(funcionario_cpf: str) -> list[dict]:
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT a.id AS atendimento_id, p.id AS paciente_id, p.nome, 
                       a.funcao, a.iniciado_em
                FROM tb_atendimentos a
                JOIN tb_pacientes p ON p.id = a.paciente_id
                WHERE a.funcionario_cpf = %s
                  AND a.status = 'ABERTO'
                ORDER BY a.iniciado_em DESC
            """,
                (funcionario_cpf,),
            )
            return cur.fetchall()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
