import bcrypt
from model.database import get_connection
from utils.helpers import only_digits
from model.funcionario_model import FuncionarioModel


class UsuarioPSModel:
    @staticmethod
    def user_exists(cpf: str) -> bool:
        cpf = only_digits(cpf)
        sql = "SELECT 1 FROM tb_usuarios_ps WHERE cpf=%s LIMIT 1"
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (cpf,))
            return cur.fetchone() is not None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def create_user(
        cpf, senha_plana
    ) -> dict:  # O cpf tem que estar na tb_funcionarios_hospital
        cpf = only_digits(cpf)
        if not FuncionarioModel.exists_cpf(cpf):
            return {
                "ok": False,
                "msg": "CPF inválido (não consta no cadastro do hospital).",
            }
        if UsuarioPSModel.user_exists(cpf):
            return {"ok": False, "msg": "Usuário já cadastrado no PS."}

        senha_hash = bcrypt.hashpw(
            senha_plana.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        sql = "INSERT INTO tb_usuarios_ps (cpf, senha_hash) VALUES (%s, %s)"
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (cpf, senha_hash))
            conn.commit()
            return {"ok": True, "msg": "Usuário cadastrado com sucesso!"}
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def verify_login(cpf, senha_plana) -> dict:
        cpf = only_digits(cpf)
        sql = """
        SELECT u.cpf, u.senha_hash, f.nome, f.funcao, f.especialidade_id
        FROM tb_usuarios_ps u
        JOIN tb_funcionarios_hospital f ON f.cpf = u.cpf
        WHERE u.cpf = %s            
        """
        conn = cur = None
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (cpf,))
            row = cur.fetchone()
            if not row:
                return {"ok": False, "msg": "Usuário não encontrado!"}

            if not bcrypt.checkpw(
                senha_plana.encode("utf-8"), row["senha_hash"].encode("utf-8")
            ):
                return {"ok": False, "msg": "Senha incorreta."}

            # Se der certo: retorna dados úteis para a view / controller
            return {
                "ok": True,
                "msg": "Login ok.",
                "usuario": {
                    "cpf": row["cpf"],
                    "nome": row["nome"],
                    "funcao": row["funcao"],  # para medico, enfermeiro e tec
                    "especialidade_id": row[
                        "especialidade_id"
                    ],  # util para os filtros dos medicos
                },
            }
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
