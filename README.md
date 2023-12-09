# Aplicação de Visão Computacional em Câmeras de Segurança para Análise Estratégica de Clientes no Ambiente Varejista

## Sumário

1. [Introdução](#introdução)
2. [Principais Tecnologias Utilizadas](#principais-tecnologias-utilizadas)
3. [Funcionalidades Principais](#funcionalidades-principais)
    1. [CRUD de Câmeras](#crud-de-câmeras)
    2. [Visualizações em Tempo Real](#visualizações-em-tempo-real)
        1. [Mapa de Calor](#mapa-de-calor)
        2. [Contagem de Pessoas](#contagem-de-pessoas)
    3. [Geração de Relatórios](#geração-de-relatórios)
4. [Como Utilizar](#como-utilizar)
5. [Licença](#licença)

## Introdução

Este repositório contém uma aplicação de visão computacional para câmeras de segurança, focada na análise estratégica de clientes no ambiente varejista. Este projeto integra diversas tecnologias para oferecer funcionalidades avançadas e insights valiosos para o gerenciamento de estabelecimentos comerciais. 
O projeto foi desenvolvido como trabalho de conclusão de curso de Técnologo em Análise e Desenvolvimento de Sistemas no Instituto Federal de Educação, Ciência e Tecnologia Farroupilha - Campus São Vicente do Sul.

## Principais Tecnologias Utilizadas

- **Frontend:**
  - HTML
  - CSS
  - JavaScript
  - Bootstrap

- **Backend:**
  - Python
  - Flask

- **Banco de Dados:**
  - MongoDB

- **Visão Computacional:**
  - OpenCV
  - YOLO

- **Conteinerização:**
  - Docker

## Funcionalidades Principais

### CRUD de Câmeras
Operações básicas de um CRUD para gerenciar as câmeras de segurança, incluindo adição, edição, exclusão e visualização.

### Visualizações em Tempo Real

#### Mapa de Calor
Acompanhamento do movimento e a concentração de clientes em tempo real através de um mapa de calor intuitivo.

#### Contagem de Pessoas
Obtenção de estatísticas precisas com a contagem de pessoas em tempo real, proporcionando insights valiosos sobre o fluxo de clientes.

### Geração de Relatórios
O sistema tem a capacidade de gerar relatórios personalizados, permitindo a análise da quantidade de clientes que entraram no estabelecimento ao longo de um período de tempo selecionado.

## Como Utilizar

Siga as etapas abaixo para configurar e executar o projeto localmente:

1. **Clone o repositório:**

```shell
git clone https://github.com/dhDSouza/tcc-computer-vision.git
```

2. **Instale as dependências:**

```shell
pip install -r requirements.txt
```

3. **Execute o MongoDB usando o Docker Compose:**

Certifique-se de ter o Docker instalado em sua máquina. Em seguida, execute o seguinte comando em seu terminal na pasta raiz do projeto onde contém  o arquivo `docker-compose.yaml`:

```shell
docker-compose up -d
```

4. **Configure as variáveis de ambiente:**

Crie um arquivo `.env` e preencha as informações de configuração, se necessário.

```shell
MONGO_URI = 'mongodb://localhost:27017/nome do banco'
SECRET_KEY = 'chave aleatória'
```
`MONGO_URI`: String de conexão com o banco de dados, neste projeto está sendo utilizado `MongoDB` então apenas coloque o nome do banco ao final da string.
`SECRET_KEY`: Insira uma chave aleatória, esta variável é necessária para o uso de sessões.

5. **Execute o servidor Flask com o comando:**

```shell
flask run
```

Isso iniciará a aplicação Flask, e você poderá acessar a interface web através do navegador.

## Licença

Este projeto está licenciado nos termos da Licença MIT. Consulte o arquivo [LICENSE](LICENSE) para obter mais informações.
