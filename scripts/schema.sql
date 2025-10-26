-- Scrip MVP para criação do banco de dados e tabelas do projeto
set names utf8mb4;
set time_zone = '+00:00';
create database if not exists db_pojeto_ps_bd2 use db_pojeto_ps_bd2;
-- Tabelas
create table if not exists tb_especialidades (
    id int auto_increment primary key,
    nome varchar(50) not null
) ENGINE = InnoDB;
-- Base do hospital, quem já existe no cadastro geral
-- Necessário para acessar o sistema do PS
create table if not exists tb_funcionarios_hospital (
    cpf char(11) primary key,
    nome varchar(120) not null,
    funcao enum('MEDICO', 'ENFERMEIRO', 'TEC_ENF') not null,
    especialidade_id int null,
    -- Somente para médicos
    criado_em timestamp default current_timestamp,
);
Engine = InnoDB;
add constraint fk_fh_especialidade foreign key (especialidade_id) references tb_especialidades(id) on update cascade on delete
set null;
ENGINE = InnoDB;
-- Para as contas que já logaram no PS (senha)
-- Regra: Só pode existir se o CPF já estiver em funcionarios_hospital
create table if not exists tb_usuarios_ps (
    id int auto_increment primary key,
    cpf char(11) not null unique,
    senha_hash varchar(255) not null,
    criado_em timestamp default current_timestamp,
    atualizado_em timestamp default current_timestamp on update current_timestamp
) ENGINE = InnoDB;
add constraint fk_usrps_fh foreign key (cpf) references tb_funcionarios_hospital(cpf) on update cascade on delete cascade ENGINE = InnoDB;
-- Pacientes e logística do PS
create table if not exists tb_pacientes (
    if int auto_increment primary key,
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
) ENGINE = InnoDB;
add constraint fk_pac_especialidade_req foreign key (especialidade_req_id) references especialidades(id) on update cascade on delete
set null ENGINE = InnoDB;

-- Tec_enf que faz as triagens