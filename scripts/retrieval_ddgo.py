import pandas as pd
import psycopg2
import sys
import os
import argparse
from datetime import datetime


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
# 2️⃣ Adicionar modules ao sys.path
# -------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pasta scripts/
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
MODULES_DIR = os.path.join(BASE_DIR, '..', 'modules')
OUTPUT_DIR = os.path.join(BASE_DIR, '..', 'out')


# Adicionar modules ao sys.path para poder importar
sys.path.append(MODULES_DIR)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))
from search_engines import DuckDuckGoSearchEngine, TitleRefiner
from embedder import HuggingFaceEmbedder


# -------------------------------
# 3️⃣ Carregar CSVs
# -------------------------------
fake_csv_path = os.path.join(DATA_DIR, 'Fake.csv')
true_csv_path = os.path.join(DATA_DIR, 'True.csv')
fake_df = pd.read_csv(fake_csv_path)
true_df = pd.read_csv(true_csv_path)
fake_df['class'] = 'fake'
true_df['class'] = 'true'
df = pd.concat([fake_df, true_df], axis=0)
df = df.drop_duplicates(subset='title')

# -------------------------------
# 4️⃣ Shuffle fixo e criar shuffle_id
# -------------------------------
df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
df_shuffled['shuffle_id'] = df_shuffled.index  # índice do shuffle fixo

# -------------------------------
# 5️⃣ Selecionar intervalo
# -------------------------------
if end_id is None:
    end_id = len(df_shuffled)
sample_df = df_shuffled[(df_shuffled['shuffle_id'] >= start_id) & (df_shuffled['shuffle_id'] < end_id)]
print(f"[INFO] Processando {len(sample_df)} títulos (shuffle_id {start_id} -> {end_id})")

# -------------------------------
# 6️⃣ Configurar TitleRefiner e SearchEngine
# -------------------------------
title_refiner = TitleRefiner(
    embedder=HuggingFaceEmbedder(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    similarity_threshold=0.85
)
search_engine = DuckDuckGoSearchEngine(title_refiner)

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
            r.get('refined_title'),
            r.get('snippet'),
            r.get('link'),
            r.get('domain'),
            shuffle_id  # novo campo
        )
        for r in results
    ]

    # Inserção em batch
    if records_to_insert:
        try:
            cur.executemany("""
                INSERT INTO retrieved_news_ddgo (
                    search_title,
                    original_title,
                    refined_title,
                    snippet,
                    link,
                    domain,
                    shuffle_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
    report_path = os.path.join(OUTPUT_DIR, 'failed_titles_report_{now_str}.csv')
    print(f"[INFO] Relatório de falhas salvo em: {report_path}")

print(f"[RESUMO] Títulos processados com sucesso: {success_count}")
print(f"[RESUMO] Títulos que falharam: {len(failed_titles)}")
