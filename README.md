# Portal Saída Segura - Colégio Carbonell


## Sobre o Projeto

O **Portal Saída Segura** é uma aplicação web desenvolvida para otimizar e digitalizar o processo de liberação de alunos fora do horário padrão no Colégio Carbonell. O objetivo principal é fornecer à equipe da portaria e secretaria uma ferramenta ágil e segura para consultar as autorizações de retirada e registrar todas as saídas de forma auditável, sem alterar o sistema de gestão principal (Sophia).

Este projeto foi desenvolvido utilizando Python com o microframework Flask, e se integra com a API do sistema Sophia para consulta de dados em tempo real.

---

## Funcionalidades Principais

* **Busca de Alunos:** Permite que o atendente busque um aluno pelo nome para iniciar o processo de liberação.
* **Visualização de Autorizados:** Exibe uma lista clara e visual das pessoas autorizadas a retirar o aluno, incluindo nome e foto (quando disponível no sistema Sophia).
* **Registro de Saída:** Um formulário simples permite que o atendente confirme a saída, registrando o nome do responsável, a data/hora, o nome do próprio atendente e observações. Os dados são salvos em um banco de dados próprio da aplicação.
* **Painel Administrativo:** Uma área de acesso restrito por senha para a coordenação.
* **Histórico de Saídas:** Acesso a uma tabela com todos os registros de saída, com filtros por nome do aluno e por data, para fins de auditoria e controle.

---

## Tecnologias Utilizadas

* **Backend:** Python 3, Flask, Flask-SQLAlchemy
* **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2
* **Banco de Dados:**
    * Desenvolvimento: SQLite
    * Produção: PostgreSQL
* **Servidor de Produção:** Gunicorn
* **Hospedagem:** Render
* **Controle de Versão:** Git & GitHub

---

## Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e rodar a aplicação no seu computador.

### Pré-requisitos
* Python 3.10 ou superior
* Git

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SeuUsuario/portal-saida-segura.git](https://github.com/SeuUsuario/portal-saida-segura.git)
    cd portal-saida-segura
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuração

1.  Na raiz do projeto, crie um arquivo chamado `.env`.
2.  Copie o conteúdo do arquivo `.env.example` (ou use o modelo abaixo) para o seu novo arquivo `.env` e preencha com as credenciais corretas.

    ```env
    # Credenciais para a API do Sophia
    SOPHIA_TENANT="SEU_TENANT_ID"
    SOPHIA_API_HOSTNAME="portal.sophia.com.br"
    SOPHIA_USER="SEU_USUARIO_DA_API"
    SOPHIA_PASSWORD="SUA_SENHA_DA_API"

    # Credenciais da Aplicação
    ADMIN_PASSWORD="defina_uma_senha_forte_para_o_admin"
    SECRET_KEY="gere_uma_chave_longa_e_aleatoria" # Use `python -c "import secrets; print(secrets.token_hex(32))"` para gerar
    ```

### Executando a Aplicação

1.  Com o ambiente virtual ativado e o arquivo `.env` configurado, inicie o servidor Flask:
    ```bash
    python app.py
    ```
2.  Abra seu navegador e acesse `http://127.0.0.1:5000`.

---

## Hospedagem

A aplicação está hospedada na plataforma **Render**. O deploy é contínuo a partir da branch `main` do repositório no GitHub. As variáveis de ambiente foram configuradas diretamente no painel do serviço web no Render.

## Limitações da Versão Atual (Hospedagem Gratuita)

Esta versão 1.0 está hospedada no plano gratuito do Render, o que é excelente para validação e uso inicial. No entanto, é importante estar ciente das seguintes limitações:

1.  **"Adormecimento" (Sleep) da Aplicação:** O serviço web do plano gratuito "dorme" após 15 minutos de inatividade. Isso significa que o primeiro acesso do dia pode ter uma lentidão inicial de 30 a 50 segundos enquanto o servidor "acorda". Após esse primeiro carregamento, a aplicação se torna rápida e responsiva para os acessos subsequentes.

2.  **Expiração do Banco de Dados:** O banco de dados PostgreSQL do plano gratuito do Render **expira e é permanentemente excluído após 90 dias**. Para garantir a continuidade do serviço e a integridade dos dados de histórico a longo prazo, será necessário fazer o upgrade do serviço de Banco de Dados para um plano pago antes do final desse período. O serviço web, por sua vez, pode continuar no plano gratuito.

