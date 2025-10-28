from model.database import get_connection
from utils.helpers import only_digits


class FuncionarioModel:
    @staticmethod
    def get_by_cpf(cpf: str):
        sql = """
        SELECT cpf, nome, funcao, especialidade_id
        FROM tb_funcionarios_hospital
        WHERE cpf = %s
        """
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (cpf,))
            return cur.fetchone()  # para dict ou none
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def exists_cpf(cpf: str) -> bool:
        return FuncionarioModel.get_by_cpf(cpf) is not None
