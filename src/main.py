from model.database import ping
from model.usuario_model import UsuarioPSModel
from model.paciente_model import PacienteModel
from model.triagem_model import TriagemModel
from model.listas_model import ListasModel
from model.atendimento_model import AtendimentoModel


def teste_simples():  # Teste de conexão com o banco de dados, cadastro e de login
    print("Ping DB: ", "OK" if ping() else "Falhou")

    cpf_tecnico = "333.333.333-33"  # Já criado
    senha = "123456"

    print("\nCadastro de usuário do PS")
    res = UsuarioPSModel.create_user(cpf_tecnico, senha)
    print(res)

    print("\nLogin")
    res2 = UsuarioPSModel.verify_login(cpf_tecnico, senha)
    print(res2)


# if __name__ == "__main__":
#     teste_simples()


def teste_fluxo():  # Cria uma triagem e a seção 'meus atendimentos'
    print("Ping DB:", "OK" if ping() else "Falhou")

    # Cadastra usuário do PS (técnico já existente na base do hospital)
    cpf_tecnico = "33333333333"
    senha = "123456"
    print("\n== Cadastro de usuário do PS ==")
    print(UsuarioPSModel.create_user(cpf_tecnico, senha))

    print("\n== Login do técnico ==")
    print(UsuarioPSModel.verify_login(cpf_tecnico, senha))

    # Cria o paciente (mínimo para rodar)
    print("\nCriar paciente")
    r = PacienteModel.create(
        nome="Paciente X",
        especialidade_req_id=2,  # Teste com a cardiologia
        leito="A-12",  # Teste para o leito
    )
    print(r)
    paciente_id = r.get("paciente_id")

    # Triagem do técnico
    print("\nTriagem")
    print(
        TriagemModel.create(
            paciente_id=paciente_id,
            tecnico_cpf=cpf_tecnico,
            sintomas="Falta de ar e dor torácica",
            prioridade="ALTA",
            pa="130x85",
            pulso=92,
            saturacao=95,
            temperatura_c=37.2,
            historico_medico="Alérgico a penicilina",
        )
    )

    # Cria as listas: médico vê somente sua especialidade
    medico_cpf = "11111111111"  # Exemplo: Dr. João - Cardiologia
    print("\nLista do médico (Cardiologia)")
    print(ListasModel.pacientes_para_medico(medico_cpf))

    print("\nLista do enfermeiro")
    print(ListasModel.pacientes_para_enfermeiro())

    # Abre o atendimento para o médico
    print("\nAbrir atendimento (médico)")
    print(AtendimentoModel.abrir(paciente_id, medico_cpf, "MEDICO"))

    # Aqui, o paciente deve sumir da lista de outros médicos, e aparecer em 'meus atendimentos'
    print("\nMeus atendimentos (médico)")
    print(ListasModel.meus_atendimentos_abertos(medico_cpf))


if __name__ == "__main__":
    teste_fluxo()
