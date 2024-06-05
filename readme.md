# MedTrack

MedTrack é uma aplicação open-source de controle de estoque e movimentações de medicamentos, desenvolvida para auxiliar os times médicos que estão atuando nas enchentes do Rio Grande do Sul.

## Funcionalidades

- Cadastro de novos medicamentos.
- Controle de quantidade de medicamentos em estoque.
- Registro de retiradas de medicamentos, incluindo quantidade retirada, observações e data/hora.
- Geração de relatórios de retiradas em formato PDF, filtrados por período.
- Autocompletar para nomes de medicamentos ao cadastrar ou buscar.
- Deleção de medicamentos com confirmação.
- Navegação intuitiva com teclas de direção e seleção de itens.

## Tecnologias Utilizadas

- Python
- PyQt5
- SQLite
- Pandas
- ReportLab

## Instalação

1. Clone o repositório:

    ```bash
    git clone https://github.com/giacomeli/MedTrack.git
    cd medtrack
    ```

2. Crie e ative um ambiente virtual:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate  # Windows
    ```

3. Instale as dependências:

    ```bash
    pip install -
