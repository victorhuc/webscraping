from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

# Configuração do Selenium para rodar sem abrir o navegador
options = Options()
options.add_argument("--headless")  # Rodar sem abrir o navegador
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920x1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)

# Inicializa o WebDriver do Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# URL da página de editais
url = (
    "https://www.joinville.sc.gov.br/editalpublico?"
    "acao=1&dt_habilitacao_ini=&nr_edital=&cod_secretaria=&"
    "ref_cod_modalidade=&ref_cod_natureza=3&ref_cod_situacao=&keyword="
)

# Acessa a página
driver.get(url)

# Espera um pouco para garantir que a página carregue completamente
time.sleep(10)

# Captura o HTML atualizado
html_pagina = driver.page_source

# Fecha o Selenium
driver.quit()

# Analisa o HTML com BeautifulSoup
soup = BeautifulSoup(html_pagina, "html.parser")

# 🔹 Encontrar todas as licitações na página
licitacoes = soup.find_all("h3")  # Números de edital
titulos = soup.find_all("span", class_="download-desc_edital")  # Títulos
tabelas = soup.find_all("table")  # Tabelas com detalhes

# 🔹 Armazena todas as licitações extraídas
dados_licitacoes = []

# 🚨 Limitar para apenas os 10 primeiros resultados
max_itens = 10
total_licitacoes = len(licitacoes)
limite = min(max_itens, total_licitacoes)

for i in range(limite):
    numero_edital = licitacoes[i].text.strip() if i < len(licitacoes) else "Não encontrado"
    titulo_edital = titulos[i].text.strip() if i < len(titulos) else "Não encontrado"

    detalhes = {}
    if i < len(tabelas):
        linhas = tabelas[i].find_all("tr")  # Pega todas as linhas da tabela
        if len(linhas) > 1:  # Garante que tem dados na tabela
            ths = [th.text.strip() for th in linhas[0].find_all("th")]  # Cabeçalhos
            tds = [td.text.strip() for td in linhas[1].find_all("td")]  # Valores

            if len(ths) == len(tds):  # Confere se há pares TH-TD
                detalhes = dict(zip(ths, tds))

    dados_licitacoes.append(
        {
            "Número do Edital": numero_edital,
            "Título": titulo_edital,
            "Detalhes": detalhes,
        }
    )

# 📝 Exibir um resumo no log (ajuda na Action)
print(f"✅ Total original de licitações encontradas: {total_licitacoes}")
print(f"✅ Licitações processadas (limitadas): {len(dados_licitacoes)}")

for licitacao in dados_licitacoes:
    print("\n📌 Número do Edital:", licitacao["Número do Edital"])
    print("📌 Título:", licitacao["Título"])

    if licitacao["Detalhes"]:
        print("\n📌 Detalhes:")
        for chave, valor in licitacao["Detalhes"].items():
            print(f"- {chave}: {valor}")
    else:
        print("❌ Nenhuma informação de tabela encontrada.")

    print("-" * 40)  # Separação entre licitações

# 💾 Gerar o arquivo JSON para o GitHub Actions pegar como artefato
with open("licitacoes.json", "w", encoding="utf-8") as f:
    json.dump(dados_licitacoes, f, ensure_ascii=False, indent=2)

print("\n✅ Arquivo 'licitacoes.json' gerado com sucesso.")
