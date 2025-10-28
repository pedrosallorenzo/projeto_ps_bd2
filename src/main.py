from model.database import ping
from model.usuario_model import UsuarioPSModel


def teste_simples():
    print("Ping DB: ", "OK" if ping() else "Falhou")

    cpf_tecnico = "333.333.333-33"  # Já criado
    senha = "123456"

    print("\nCadastro de usuário do PS")
    res = UsuarioPSModel.create_user(cpf_tecnico, senha)
    print(res)

    print("\nLogin")
    res2 = UsuarioPSModel.verify_login(cpf_tecnico, senha)
    print(res2)


if __name__ == "__main__":
    teste_simples()
