## Requisitos
- Python 3.6+
- pip
- Conexão com a internet

## Preparação
```
python -m venv .venv
source .venv/bin/activate (Linux)
.venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

Edite o arquivo `.env` com as informações necessárias. Exemplo:
```
DISCORD_WEBHOOK=https://discord.com/api/webhooks/1234567890/ABCDEFGHIJKLMN
```

O arquivo sqlite3 com a estrutura da base de dados já está no repositório. Mas caso queira criar um novo arquivo, basta rodar o comando SQL abaixo:
```
CREATE TABLE "ingressantes" (
	"id"	INTEGER,
	"uniqueId"	TEXT NOT NULL UNIQUE,
	"curso"	TEXT,
	"nome"	TEXT,
	"semIngresso"	TEXT,
	"comDocs"	TEXT,
	"aptoMatricula"	TEXT,
	"matriculado"	TEXT,
	"drgca"	TEXT,
	"cor"	TEXT,
	"deficiencia"	TEXT,
	"quilombola"	TEXT,
	"social"	TEXT,
	"geral"	TEXT,
	"hash"	TEXT,
	"lastUpdated"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
```

## Execução
```
python main.py
```

## Estrutura
```
.
├── .venv
├── .env
├── .gitignore
├── database.db
├── main.py
├── README.md
└── requirements.txt
```

## Observações
- O arquivo `.env` não deve ser versionado.
- O arquivo `database.db` é a base de dados sqlite3.
- O arquivo `main.py` é o script principal.
- O arquivo `.gitignore` contém os arquivos e diretórios que não devem ser versionados.
- O arquivo `requirements.txt` contém as dependências do projeto.
- O diretório `.venv` é o ambiente virtual do Python.
- Este é um simples script para fins educacionais, não está otimizado (uso de POO, bibliotecas, módulos e etc) e não deve ser usado em produção.