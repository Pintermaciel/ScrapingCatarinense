# scraping_catarinense  

**scraping_catarinense** é um projeto de scraping desenvolvido para extrair dados do site das Drogarias Catarinense. O objetivo principal é coletar informações sobre medicamentos, seus preços e mapear a estrutura mercadológica do site, como categorias e subcategorias.  

## Objetivos  
- **Medicamentos e preços:** Obter detalhes de produtos, como nome, descrição e valores.  
- **Estrutura mercadológica:** Mapear categorias e subcategorias, organizando a hierarquia do site.  

## Funcionalidades  
- Extração de dados de produtos e preços.  
- Coleta de categorias e subcategorias associadas aos produtos.  
- Exportação de dados para formatos como CSV ou JSON.  
- Configuração de scraping com suporte a páginas dinâmicas, se necessário.  

---

## Tecnologias utilizadas  
- **Python**: Linguagem principal.  
- **Bibliotecas:**  
  - `requests`: Realiza requisições HTTP para capturar páginas HTML.  
  - `BeautifulSoup` ou `lxml`: Realiza parsing e extração de dados de HTML.  
  - `pandas`: Manipulação e armazenamento de dados estruturados.  
  - `selenium` (opcional): Lida com páginas que dependem de JavaScript para carregar conteúdo.  
- **Poetry**: Gerenciador de dependências e ambientes virtuais.  

---

## Estrutura do projeto  
```plaintext
scraping_catarinense/
│
├── data/                 # Dados extraídos
├── src/                  # Código-fonte
│   ├── scraper.py        # Lógica principal de scraping
│   ├── parser.py         # Processamento e limpeza dos dados
│   ├── categories.py     # Extração da estrutura de categorias
│   ├── storage.py        # Funções para salvar os dados
│   └── utils.py          # Funções auxiliares
├── pyproject.toml        # Configuração do Poetry
├── README.md             # Documentação
└── .env.example          # Exemplo de variáveis de ambiente

Configuração
Clone o repositório:

bash
Copiar código
git clone https://github.com/seuusuario/scraping_catarinense.git
cd scraping_catarinense
Instale o Poetry (caso não tenha):

bash
Copiar código
curl -sSL https://install.python-poetry.org | python3 -
Configure as dependências do projeto:

bash
Copiar código
poetry install
Ative o ambiente virtual gerenciado pelo Poetry:

bash
Copiar código
poetry shell
Configure o arquivo .env (baseado no modelo .env.example) com as variáveis necessárias:

URL base do site.
Configurações de user-agent, caso necessário.
Execute o script principal:

bash
Copiar código
python src/scraper.py
Os dados serão salvos na pasta data/.

Exemplo de saída
Produtos e preços:

json
Copiar código
[
  {
    "nome": "Paracetamol 500mg",
    "preco": 12.99,
    "categoria": "Analgésicos",
    "subcategoria": "Dor e Febre"
  }
]
Estrutura de categorias:

json
Copiar código
{
  "categoria": "Medicamentos",
  "subcategorias": [
    "Analgésicos",
    "Antiinflamatórios",
    "Antibióticos"
  ]
}
