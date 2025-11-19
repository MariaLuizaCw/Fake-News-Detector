#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Carrega variáveis do .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DATA_DIR = os.path.join(BASE_DIR, '..', '..', 'data')
MODULES_DIR = os.path.join(BASE_DIR, '..', '..', 'modules')


# Adiciona o path para importar a LLM (duas pastas acima)
sys.path.append(MODULES_DIR)
from llm_base import LLM  # ajuste o nome do arquivo se necessário



def load_shuffle_classes(data_dir):
    """Carrega os CSVs Fake/True e retorna um dict shuffle_id -> true_class"""
    fake_df = pd.read_csv(os.path.join(data_dir, 'Fake.csv'))
    true_df = pd.read_csv(os.path.join(data_dir, 'True.csv'))
    fake_df['class'] = 'fake'
    true_df['class'] = 'real'
    df = pd.concat([fake_df, true_df], axis=0).drop_duplicates(subset='title')
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df_shuffled['shuffle_id'] = df_shuffled.index
    # Mapeia shuffle_id para a classe verdadeira
    return df_shuffled.set_index('shuffle_id')['class'].to_dict()


def main(test_name: str, start_id: int = 0, end_id: int = None):
    # Conexão com o banco usando SQLAlchemy
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    # Carrega mapeamento shuffle_id -> true_class
    shuffle_to_class = load_shuffle_classes(DATA_DIR)

    # Tabela de prompts
    table_name = f"{test_name}_prompts"
    query = f"SELECT * FROM {table_name} ORDER BY shuffle_id;"

    print('Search table', table_name)
    with engine.begin() as conn: 
        result = conn.execute(text(query))
        rows = result.fetchall()  # pega todos de uma vez
        prompts_data = [dict(row._mapping) for row in rows]
        # Filtra no Python pelo shuffle_id
        if start_id is not None:
            prompts_data = [row for row in prompts_data if row['shuffle_id'] >= start_id]
        if end_id is not None:
            prompts_data = [row for row in prompts_data if row['shuffle_id'] < end_id]

        # Cria tabela de resultados se não existir (agora com true_class)
        results_table = f"{test_name}_results"
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {results_table} (
                id SERIAL PRIMARY KEY,
                search_title TEXT,
                shuffle_id INT,
                response TEXT,
                true_class TEXT
            );
        """))

        res = conn.execute(text(f"SELECT shuffle_id FROM {results_table};"))
        existing_ids = {row[0] for row in res.fetchall()}

        prompts_data = [row for row in prompts_data if row['shuffle_id'] not in existing_ids]

    # Inicializa a LLM Groq
    groq_llm = LLM(
        model="llama-3.1-8b-instant",
        api_key_env="GROQ_API_KEY",
        endpoint="https://api.groq.com/openai/v1/chat/completions"
    )

    # Processa cada prompt e salva no banco
    with engine.connect() as conn:  # begin() garante commit automático
        for idx, row in enumerate(prompts_data, 1):
            prompt = row.get('prompt')
            search_title = row.get('search_title')
            shuffle_id = row.get('shuffle_id')
            true_class = shuffle_to_class.get(shuffle_id, None)

            try:
                response = groq_llm.generate(prompt)
                print(f"\nPrompt {idx} (shuffle_id={shuffle_id}):")
                print(f"Resposta: {response} | Classe real: {true_class}")

                # Insere no banco
                conn.execute(
                    text(f"""
                        INSERT INTO {results_table} 
                        (search_title, shuffle_id, response, true_class) 
                        VALUES (:search_title, :shuffle_id, :response, :true_class)
                    """),
                    {
                        "search_title": search_title,
                        "shuffle_id": shuffle_id,
                        "response": response,
                        "true_class": true_class
                    }
                )
                conn.commit() 
            except Exception as e:
                print(f"Erro ao processar prompt {idx} (shuffle_id={shuffle_id}): {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processa prompts de um teste usando LLM")
    parser.add_argument("test_name", type=str, help="Nome do teste (prefixo da tabela de prompts)")
    parser.add_argument("--start_id", type=int, default=0, help="ID inicial do shuffle para processar")
    parser.add_argument("--end_id", type=int, default=None, help="ID final do shuffle para processar")
    args = parser.parse_args()

    print('Executing test name', args.test_name)
    main(args.test_name, args.start_id, args.end_id)
