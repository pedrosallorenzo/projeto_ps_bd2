import pytest
from model.paciente_model import PacienteModel
from model.triagem_model import TriagemModel


def test_cria_paciente_triagem(monkeypatch):
    r = PacienteModel.create(nome="Teste py", especialidade_req_id=2, leito="B-01")
    assert r["ok"]
    pid = r["paciente_id"]

    t = TriagemModel.create(pid, "33333333333", "Dor torácica", "ALTA")
    assert t["ok"]
