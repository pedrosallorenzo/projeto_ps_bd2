-- Limpa todos os dados de trabalho sem apagar a base, funcionários e especialidades

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE tb_internacoes;
TRUNCATE TABLE tb_atendimentos;
TRUNCATE TABLE tb_prontuarios;
TRUNCATE TABLE tb_triagem;
TRUNCATE TABLE tb_paciente;

ALTER TABLE tb_internacoes AUTO_INCREMENT = 1;
ALTER TABLE tb_atendiemntos AUTO_INCREMENT = 1;
ALTER TABLE tb_prontuarios AUTO_INCREMENT = 1;
ALTER TABLE tb_triagem AUTO_INCREMENT = 1;
ALTER TABLE tb_paciente AUTO_INCREMENT = 1;

SET FOREIGN_KEY_CHECKS = 1;

-- Pacientes de exemplo
INSERT INTO tb_pacientes (nome, especialidade_req_id, status_ps) VALUES ('Paciente Demo', 2, 'AGUARDANDO');