-- Scrip MVP para criação do banco de dados e tabelas do projeto
set names utf8mb4;
set time_zone = '+00:00';
create database if not exists db_projeto_ps_bd2;
use db_projeto_ps_bd2;

-- Tabelas
create table if not exists tb_especialidades (  
    id int auto_increment primary key,
    nome varchar(50) not null
);

-- Base do hospital, quem já existe no cadastro geral
-- Necessário para acessar o sistema do PS
create table if not exists tb_funcionarios_hospital (
    cpf char(11) primary key,
    nome varchar(120) not null,
    funcao enum('MEDICO', 'ENFERMEIRO', 'TECNICO_DE_ENFERMAGEM') not null,
    especialidade_id int null,
    -- Somente para médicos
    criado_em timestamp default current_timestamp
);

Alter table tb_funcionarios_hospital add constraint fk_fh_especialidade 
foreign key (especialidade_id) references tb_especialidades(id) 
on update cascade on delete set null;

-- Para as contas que já logaram no PS (senha)
-- Regra: Só pode existir se o CPF já estiver em funcionarios_hospital
create table if not exists tb_usuarios_ps (
    id int auto_increment primary key,
    cpf char(11) not null unique,
    senha_hash varchar(255) not null,
    criado_em timestamp default current_timestamp,
    atualizado_em timestamp default current_timestamp on update current_timestamp
);
Alter table tb_usuarios_ps add constraint fk_usrps_fh 
foreign key (cpf) references tb_funcionarios_hospital(cpf) 
on update cascade on delete cascade;

-- Pacientes e logística do PS
create table if not exists tb_pacientes (
    id int auto_increment primary key,
    nome varchar(120) not null,
    cpf char(11) null unique,
    -- Para os casos que chegam de ambulância
    telefone varchar(20) null,
    data_nascimento date null,
    tipo_sanguineo enum('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') null,
    especialidade_req_id int null,
    -- Para a especialidade que foi requisitada pelo paciente
    leito varchar(20) null,
    -- Pode ser alterado
    status_ps enum(
        'AGUARDANDO',
        'EM_ATENDIMENTO',
        'INTERNADO',
        'ALTA'
    ) not null default 'AGUARDANDO',
    criado_em timestamp default current_timestamp,
    atualizado_em timestamp default current_timestamp on update current_timestamp
);
Alter table tb_pacientes add constraint fk_pac_especialidade_req 
foreign key (especialidade_req_id) references tb_especialidades(id) 
on update cascade on delete set null;

-- Tec_enf faz as triagens
create table tb_triagens
(id INT AUTO_INCREMENT PRIMARY KEY,
paciente_id INT NOT NULL,
tecnico_cpf CHAR(11) NOT NULL,
-- sinais vitais
pa VARCHAR(15) NULL,                 -- pressão arterial (texto: "120x80")
pulso SMALLINT NULL,
saturacao TINYINT NULL,
temperatura_c DECIMAL(4,1) NULL,
historico_medico TEXT NULL,
sintomas TEXT NOT NULL,
prioridade ENUM('LEVE','MODERADA','ALTA') NOT NULL,
criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

alter table tb_triagens add constraint fk_tri_paciente
Foreign Key (paciente_id) REFERENCES tb_pacientes(id)
on update cascade on DELETE cascade;

alter table tb_triagens add constraint fk_tri_tecnico
Foreign Key (tecnico_cpf) REFERENCES tb_funcionarios_hospital(cpf)
on update cascade on delete restrict;

-- Prontuário
create table if NOT EXISTS tb_prontuarios
(id int AUTO_INCREMENT PRIMARY KEY,
paciente_id int not null unique,
medico_cpf char(11) not null,
historico_medico text null, -- Alterável
sintomas text null, -- Alterável
conduta text null,
diagnostico text null,
observacoes text null,
atualizado_em TIMESTAMP DEFAULT current_timestamp on update current_timestamp);

ALTER TABLE tb_prontuarios ADD CONSTRAINT fk_prt_paciente
FOREIGN KEY (paciente_id) REFERENCES tb_pacientes(id)
ON UPDATE CASCADE ON DELETE CASCADE;

alter table tb_prontuarios add constraint fk_prt_medico
Foreign Key (medico_cpf) REFERENCES tb_funcionarios_hospital(cpf)
on update cascade on delete restrict;

-- Atendimentos
-- Controla as listas que aparecem para cada médico e a sessão "meus atendimentos"
CREATE Table if not EXISTS tb_atendimentos
(id int auto_increment primary key,
paciente_id int not null,
funcionario_cpf char(11) not null, -- para medicos ou enfermeiros
funcao enum('MEDICO', 'ENFERMEIRO') not NULL,
status enum('ABERTO', 'FECHADO') not NULL DEFAULT 'ABERTO',
iniciado_em TIMESTAMP DEFAULT current_timestamp,
finalizado_em TIMESTAMP NULL);

Alter table tb_atendimentos add constraint fk_atd_paciente
Foreign Key (paciente_id) REFERENCES tb_pacientes(id)
on update cascade on delete cascade;

alter table tb_atendimentos add constraint fk_atd_func
Foreign Key (funcionario_cpf) REFERENCES tb_funcionarios_hospital(cpf)
on update cascade on delete restrict;

create INDEX idx_atd_paciente_status on tb_atendimentos (paciente_id, status);
create INDEX idx_atd_func_status on tb_atendimentos (funcionario_cpf, status);

-- Internações
-- Registra quando o médico internar o paciente
create TABLE if not EXISTS tb_internacoes
(id int auto_increment PRIMARY KEY,
paciente_id int not null UNIQUE, -- 1 internacao ativa por paciente no PS
medico_cpf char(11) not null,
motivo text null,
internado_em TIMESTAMP DEFAULT current_timestamp);

ALTER table tb_internacoes add constraint fk_int_paciente
Foreign Key (paciente_id) REFERENCES tb_pacientes(id)
on update cascade on delete cascade;

ALTER table tb_internacoes add constraint fk_int_medico
Foreign Key (medico_cpf) REFERENCES tb_funcionarios_hospital(cpf)
on update cascade on delete restrict;

-- Seeds básicos
INSERT IGNORE INTO tb_especialidades (id, nome) VALUES
  (1,'Clínica Geral'), (2,'Cardiologia'), (3,'Ortopedia');

-- Exemplo de funcionário do hospital
INSERT IGNORE INTO tb_funcionarios_hospital (cpf, nome, funcao, especialidade_id) VALUES
  ('11111111111','Dr. João Cardoso','MEDICO',2),
  ('22222222222','Enf. Maria Silva','ENFERMEIRO',NULL),
  ('33333333333','Tec. Pedro Souza','TECNICO_DE_ENFERMAGEM',NULL),
  ('44444444444','Dra. Ana Rocha','MEDICO',1);
  
  
  
-- Indices e algumas outras regras
-- Paciente por status
CREATE INDEX if not EXISTS idx_pac_status_ps on tb_pacientes (status_ps, especialidade_req_id);

-- Triagem para cada paciente
CREATE INDEX if not EXISTS idx_tri_paciente on tb_triagens (paciente_id);

-- Atendimentos (para reforçar)
CREATE INDEX if not EXISTS idx_atd_paciente_status on tb_atendimentos (paciente_id, status);
CREATE INDEX if not EXISTS idx_atd_func_status on tb_atendimentos (funcionario_id, status);



-- Testes
-- Ver especialidades
select * from tb_especialidades;

-- Ver funcionários do hospital
SELECT cpf, nome, funcao, especialidade_id FROM tb_funcionarios_hospital;

-- Criar um paciente (ambulância)
INSERT INTO tb_pacientes (nome, especialidade_req_id, status_ps, leito, tipo_sanguineo)
VALUES ('Paciente Ambulância', 2, 'AGUARDANDO', 'A-12', NULL);

-- Triagem
INSERT INTO tb_triagens (paciente_id, tecnico_cpf, pa, pulso, saturacao, temperatura_c, historico_medico, sintomas, prioridade)
VALUES (1, '33333333333', '130x85', 92, 95, 37.2, 'Alérgico a penicilina', 'Falta de ar e dor torácica', 'ALTA');

-- Abrir atendimento do médico
INSERT INTO tb_atendimentos (paciente_id, funcionario_cpf, funcao, status)
VALUES (1, '11111111111', 'MEDICO', 'ABERTO');
-- atualizar depois:
UPDATE tb_pacientes SET status_ps='EM_ATENDIMENTO' WHERE id=1;

-- Criar e atualizar o printuário
INSERT INTO tb_prontuarios (paciente_id, medico_cpf, historico_medico, sintomas, diagnostico, conduta, observacoes)
VALUES (1, '11111111111', 'Alérgico a penicilina', 'Dispneia, dor torácica', 'Insuficiência cardíaca aguda', 'Oxigênio, nitrato, monitorização', 'Avaliar eco');
-- atualizar depois:
UPDATE tb_prontuarios SET observacoes='Evolução 2h: estável' WHERE paciente_id=1;

-- Encerrar atendimento
UPDATE tb_atendimentos 
SET status='FECHADO', finalizado_em=NOW()
WHERE paciente_id=1 AND funcionario_cpf='11111111111' AND status='ABERTO';
-- atualizar depois:
UPDATE tb_pacientes SET status_ps='AGUARDANDO' WHERE id=1; -- volta para fila, se desejar

-- Internar (congela os dados e retira o leito do PS)
INSERT INTO tb_internacoes (paciente_id, medico_cpf, motivo)
VALUES (1, '11111111111', 'Risco clínico – internação em cardiologia');
-- atualizar depois:
UPDATE tb_pacientes SET status_ps='INTERNADO', leito=NULL WHERE id=1;

-- Dar alta
DELETE FROM tb_pacientes WHERE id=1;