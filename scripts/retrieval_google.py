import pandas as pd
import psycopg2
import sys
import os
import argparse
import json
import http.client
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv

# -------------------------------
# 0️⃣ Carregar .env externo
# -------------------------------
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(ENV_PATH)
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("[ERRO] GOOGLE_API_KEY não encontrada no .env")
    sys.exit(1)

# -------------------------------
# 1️⃣ Receber parâmetros
# -------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--start_id", type=int, default=0, help="ID inicial do shuffle para processar")
parser.add_argument("--end_id", type=int, default=None, help="ID final do shuffle para processar")
args = parser.parse_args()
start_id = args.start_id
end_id = args.end_id

# -------------------------------
# 2️⃣ Configurar diretórios
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
MODULES_DIR = os.path.join(BASE_DIR, '..', 'modules')
OUTPUT_DIR = os.path.join(BASE_DIR, '..', 'out')

# Adicionar modules ao sys.path
sys.path.append(MODULES_DIR)
from search_engines import GoogleSearchEngine  # assumindo que a classe está em modules/google_search.py

# -------------------------------
# 3️⃣ Carregar CSVs
# -------------------------------
fake_df = pd.read_csv(os.path.join(DATA_DIR, 'Fake.csv'))
true_df = pd.read_csv(os.path.join(DATA_DIR, 'True.csv'))
fake_df['class'] = 'fake'
true_df['class'] = 'true'
df = pd.concat([fake_df, true_df], axis=0).drop_duplicates(subset='title')

# -------------------------------
# 4️⃣ Shuffle fixo e criar shuffle_id
# -------------------------------
df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
df_shuffled['shuffle_id'] = df_shuffled.index

# -------------------------------
# 5️⃣ Selecionar intervalo
# -------------------------------
if end_id is None:
    end_id = len(df_shuffled)
sample_df = df_shuffled[(df_shuffled['shuffle_id'] >= start_id) & (df_shuffled['shuffle_id'] < end_id)]
print(f"[INFO] Processando {len(sample_df)} títulos (shuffle_id {start_id} -> {end_id})")

# -------------------------------
# 6️⃣ Inicializar SearchEngine
# -------------------------------
search_engine = GoogleSearchEngine(api_key=API_KEY)

# -------------------------------
# 7️⃣ Conectar ao Postgres
# -------------------------------
try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5436,
        dbname="database",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    print("[INFO] Conexão com Postgres realizada com sucesso")
except Exception as e:
    print(f"[ERRO] Falha ao conectar no Postgres: {e}")
    sys.exit(1)

# -------------------------------
# 8️⃣ Inicializar listas de sucesso/falha
# -------------------------------
failed_titles = []
success_count = 0

# -------------------------------
# 9️⃣ Iterar sobre os títulos
# -------------------------------
for idx, row in sample_df.iterrows():
    title_1 = row['title']
    shuffle_id = row['shuffle_id']
    print(f"[INFO] Processando shuffle_id {shuffle_id}: {title_1[:60]}...")

    try:
        results = search_engine.search(title_1, num_results=10)
    except Exception as e:
        print(f"[ERRO] Falha na busca do título: {e}")
        failed_titles.append({'title': title_1, 'shuffle_id': shuffle_id, 'reason': f'Busca falhou: {e}'})
        continue

    records_to_insert = [
        (
            title_1,
            r.get('title'),
            r.get('snippet'),
            r.get('link'),
            r.get('domain'),
            shuffle_id
        )
        for r in results
    ]

    if records_to_insert:
        try:
            cur.executemany("""
                INSERT INTO retrieved_news_google (
                    search_title,
                    original_title,
                    snippet,
                    link,
                    domain,
                    shuffle_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, records_to_insert)
            conn.commit()
            success_count += len(records_to_insert)
            print(f"[INFO] Inseridos {len(records_to_insert)} registros para shuffle_id {shuffle_id}")
        except Exception as e:
            conn.rollback()
            print(f"[ERRO] Falha ao inserir batch para shuffle_id {shuffle_id}: {e}")
            failed_titles.append({'title': title_1, 'shuffle_id': shuffle_id, 'reason': f'Insert batch falhou: {e}'})
    else:
        print(f"[AVISO] Nenhum resultado para inserir para shuffle_id {shuffle_id}")
        failed_titles.append({'title': title_1, 'shuffle_id': shuffle_id, 'reason': 'Nenhum resultado inserido'})

# -------------------------------
# 10️⃣ Fechar conexão
# -------------------------------
cur.close()
conn.close()
print("[INFO] Script finalizado com sucesso")

# -------------------------------
# 11️⃣ Criar CSV de relatório
# -------------------------------
if failed_titles:
    report_df = pd.DataFrame(failed_titles)
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(OUTPUT_DIR, f'failed_titles_report_{now_str}.csv')
    report_df.to_csv(report_path, index=False)
    print(f"[INFO] Relatório de falhas salvo em: {report_path}")

print(f"[RESUMO] Títulos processados com sucesso: {success_count}")
print(f"[RESUMO] Títulos que falharam: {len(failed_titles)}")
