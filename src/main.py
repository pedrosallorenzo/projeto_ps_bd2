from model.database import ping
from model.usuario_model import UsuarioPSModel
from model.paciente_model import PacienteModel
from model.triagem_model import TriagemModel
from model.listas_model import ListasModel
from model.atendimento_model import AtendimentoModel
from model.prontuario_model import ProntuarioModel
from model.acoes_model import AcoesModel


def fluxo_basico_criar_e_triagem() -> tuple[int, str, str]:
    # Criar e registrar a triagem
    print("Ping DB:", "OK" if ping() else "Falhou")

    cpf_tecnico = "33333333333"
    cpf_medico = "11111111111"  # Dr. João (Cardiologia)

    print("\n== Cadastro de usuário do PS (técnico) ==")
    print(UsuarioPSModel.create_user(cpf_tecnico, "123456"))

    print("\n== Login do técnico ==")
    print(UsuarioPSModel.verify_login(cpf_tecnico, "123456"))

    print("\n== Criar paciente ==")
    r_pac = PacienteModel.create(
        nome="Paciente X", especialidade_req_id=2, leito="A-12"  # Cardiologia
    )
    print(r_pac)
    paciente_id = r_pac.get("paciente_id")
    if not paciente_id:
        raise RuntimeError("Não foi possível obter paciente_id.")

    print("\n== Triagem ==")
    r_tri = TriagemModel.create(
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
    print(r_tri)

    return paciente_id, cpf_tecnico, cpf_medico


def listas_e_atendimento(paciente_id: int, cpf_medico: str):
    print("\n== Lista do médico (Cardiologia) ==")
    print(ListasModel.pacientes_para_medico(cpf_medico))

    print("\n== Lista do enfermeiro ==")
    print(ListasModel.pacientes_para_enfermeiro())

    print("\n== Abrir atendimento (médico) ==")
    print(AtendimentoModel.abrir(paciente_id, cpf_medico, "MEDICO"))

    print("\n== Meus atendimentos (médico) ==")
    print(ListasModel.meus_atendimentos_abertos(cpf_medico))


def prontuario_internacao_alta(paciente_id: int, cpf_medico: str):
    print("\n== Prontuário: abrir ==")
    print(ProntuarioModel.get_or_create(paciente_id, cpf_medico))

    print("\n== Prontuário: salvar ==")
    print(
        ProntuarioModel.salvar(
            paciente_id,
            cpf_medico,
            historico_medico="Hipertenso controlado",
            sintomas="Dispneia",
            diagnostico="Insuficiência cardíaca aguda",
            conduta="Oxigênio + nitrato",
            observacoes="Monitorar 6h",
        )
    )

    print("\n== Internar ==")
    print(AcoesModel.internar(paciente_id, cpf_medico, "Risco clínico – cardiologia"))

    print("\n== Prontuário: tentativa de salvar após internar ==")
    print(
        ProntuarioModel.salvar(
            paciente_id, cpf_medico, observacoes="Tentativa pós-internação"
        )
    )

    print("\n== Dar Alta ==")
    print(AcoesModel.dar_alta(paciente_id, cpf_medico))

    print("\n== Lista do médico (após alta) ==")
    print(ListasModel.pacientes_para_medico(cpf_medico))

    print("\n== Lista do enfermeiro (após alta) ==")
    print(ListasModel.pacientes_para_enfermeiro())


def teste_fluxo():
    paciente_id, cpf_tecnico, cpf_medico = fluxo_basico_criar_e_triagem()
    listas_e_atendimento(paciente_id, cpf_medico)
    prontuario_internacao_alta(paciente_id, cpf_medico)


if __name__ == "__main__":
    teste_fluxo()
