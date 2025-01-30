import os
import sqlite3
import requests
from hashlib import sha256
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

con = sqlite3.connect("database.db")
cur = con.cursor()

url = "https://sistemas.unifal-mg.edu.br/app/copeve/ingresso/relatorios/listageral.php"
discordWebhook = os.getenv("DISCORD_WEBHOOK")

# Não alterar, precisa estar idêntico ao site
cursos = [
    {
        "curso_formacao_turno": "INTERDISCIPLINAR EM CIÊNCIA E TECNOLOGIA - Bacharelado - Integral",
        "cod": "BICT-I"
    },
    {
        "curso_formacao_turno": "INTERDISCIPLINAR EM CIÊNCIA E TECNOLOGIA - Bacharelado - Noturno",
        "cod": "BICT-N"
    },
    {
        "curso_formacao_turno": "ENGENHARIA AMBIENTAL - Bacharelado - Integral",
        "cod": "EA"
    },
    {
        "curso_formacao_turno": "ENGENHARIA CIVIL - Bacharelado - Integral",
        "cod": "EC"
    },
    {
        "curso_formacao_turno": "ENGENHARIA DE MINAS - Bacharelado - Integral",
        "cod": "EM"
    },
    {
        "curso_formacao_turno": "ENGENHARIA DE PRODUÇÃO - Bacharelado - Integral",
        "cod": "EP"
    },
    {
        "curso_formacao_turno": "ENGENHARIA QUÍMICA - Bacharelado - Integral",
        "cod": "EQ"
    },
    {
        "curso_formacao_turno": "GESTÃO AMBIENTAL E SUSTENTABILIDADE - Bacharelado - EaD",
        "cod": "GAS"
    }
]

# Faz a requisição para cada curso e pega os dados dos alunos em lote
for curso in cursos:

    # Monta a requisição com o curso atual do loop for
    data = {
        "curso_formacao_turno": curso["curso_formacao_turno"],
        "ano": "",
        "semestre": "",
        "tipo": "html"
    }

    # Bate no site da Unifal com os dados do curso atual
    response = requests.post(url, data=data)

    # Faz a leitura e "tradução" do HTML para um objeto BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Pega a tabela com os dados dos alunos (cuidado, existem duas tabelas no site, precisamos pegar a segunda que tem a classe "tabelaZebra" e etc)
    table = soup.find("table", class_="tabelaZebra tabelaResponsiva semCabecalho")

    # Faz um loop em todas as linhas da tabela (aluno por aluno)
    for row in table.find_all("tr"):

        # Pega todas as células da linha atual
        cells = row.find_all("td")

        # Se tiver mais de 0 células, significa que é um aluno válido
        if len(cells) > 0:

            # Monta um dicionário com os dados do aluno
            aluno = {
                "curso": curso["cod"],
                "nome": cells[0].text,
                "semingres": cells[4].text,
                "comdocs": cells[5].text,
                "aptomatric": cells[6].text,
                "matriculado": cells[7].text,
                "drgca": cells[8].text,
                "cor": cells[9].text,
                "deficiencia": cells[10].text,
                "quilombola": cells[11].text,
                "social": cells[12].text,
                "geral": cells[13].text,
            }

            # Gera um hash único para o aluno, usando uma combinação de curso e nome, para garantir que não haja duplicidade
            uniqueId = sha256(f"{aluno['curso']}_{aluno['nome']}".encode("utf-8")).hexdigest()

            # Concatena todos os dados do aluno para gerar o hash, assim garantimos que qualquer mudança nos dados do aluno gere hash totalmente diferente
            concatData = "".join([aluno["nome"], aluno["semingres"], aluno["comdocs"], aluno["aptomatric"], aluno["matriculado"], aluno["drgca"], aluno["cor"], aluno["deficiencia"], aluno["quilombola"], aluno["social"], aluno["geral"]])

            # Gera o hash e adiciona ao dicionário do aluno
            aluno["hash"] = sha256(concatData.encode("utf-8")).hexdigest()

            # Adiciona o uniqueId ao dicionário do aluno
            aluno["uniqueId"] = uniqueId

            # Pega a data e hora atual para adicionar ao banco de dados
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Monta a tupla com os valores do aluno para inserir no banco de dados logo abaixo
            values = (aluno["uniqueId"], aluno["curso"], aluno["nome"], aluno["semingres"], aluno["comdocs"], aluno["aptomatric"], aluno["matriculado"], aluno["drgca"], aluno["cor"], aluno["deficiencia"], aluno["quilombola"], aluno["social"], aluno["geral"], aluno["hash"], now)

            # Verifica se o aluno já está no banco de dados
            print(f"Verificando aluno {aluno['nome']} do curso {aluno['curso']}...")
            cur.execute("SELECT * FROM ingressantes WHERE uniqueId = ?", (uniqueId,))
            result = cur.fetchone()

            # Se o aluno já estiver no banco de dados, verifica se houve mudança de status, comparando o hash atual com o hash do banco de dados
            if(result):

                # Se o hash do banco de dados for diferente do hash atual, significa que houve mudança de alguma informação do aluno
                if(result[14] != aluno["hash"]):
                    print(f"Aluno {aluno['nome']} teve mudança de informações!")

                    # Prepara uma lista onde salvaremos as mudanças que queremos acompanhar, para usarmos depois
                    changes = []

                    # Verifica se mudou o semestre de ingresso (result = banco de dados, values = dados do site)
                    if(result[4] != values[3]):
                        changes.append({
                            "field": "SEMESTRE DE INGRESSO",
                            "old": result[4],
                            "new": values[3]
                        })

                    # Verifica se mudou os status do envio de documentação
                    if(result[5] != values[4]):
                        changes.append({
                            "field": "DOCUMENTAÇÃO",
                            "old": result[5],
                            "new": values[4]
                        })

                    # Verifica se mudou o status de apto para matrícula
                    if(result[6] != values[5]):
                        changes.append({
                            "field": "APTO PARA MATRÍCULA",
                            "old": result[6],
                            "new": values[5]
                        })

                    # Verifica se mudou o status de matriculado
                    if(result[13] != values[12]):
                        changes.append({
                            "field": "STATUS GERAL",
                            "old": result[13],
                            "new": values[12]
                        })
                    
                    # Hack para remover o uniqueId da tupla, pois não queremos atualizar o uniqueId no banco de dados
                    values = values[1:]

                    # Salva as alterações encontradas no banco de dados, no mesmo uniqueId de antes
                    cur.execute("UPDATE ingressantes SET curso = ?, nome = ?, semIngresso = ?, comDocs = ?, aptoMatricula = ?, matriculado = ?, drgca = ?, cor = ?, deficiencia = ?, quilombola = ?, social = ?, geral = ?, hash = ?, lastUpdated = ? WHERE uniqueId = ?", values + (uniqueId,))
                    
                    # Prepara os parâmetros que enviaremos ao Discord Webhook
                    webhookData = {
                        "embeds": [
                            {
                                "title": "Informações atualizadas",
                                "fields": [
                                    {
                                        "name": "Nome",
                                        "value": aluno['nome']
                                    },
                                    {
                                        "name": "Curso",
                                        "value": aluno['curso']
                                    }
                                ]
                            }
                        ]
                    }

                    # Para cada mudança de interesse que encontramos, adicionamos ao embed do Discord Webhook
                    for change in changes:
                        webhookData["embeds"][0]["fields"].append({
                            "name": f"{change['field']}",
                            "value": f"**De:** {change['old']} **Para:** {change['new']}"
                        })

                    # Envia o Discord Webhook com as informações atualizadas
                    requests.post(discordWebhook, json=webhookData)                  
            else:
                # Se o aluno não estiver no banco de dados (ou seja, é a primeira vez que vemos ele), adicionamos ao banco de dados
                cur.execute("INSERT INTO ingressantes VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)

    # Salva as alterações no banco de dados em lotes, uma vez por curso, para evitar sobrecarga no banco de dados
    con.commit()