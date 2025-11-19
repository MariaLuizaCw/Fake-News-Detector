#!/usr/bin/env python3
import os
import sys
import argparse
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Adiciona o path para importar a LLM (duas pastas acima)
sys.path.append(os.path.abspath(os.path.join(__file__, "../../modules")))
from llm_module import LLM  # ajuste o nome do arquivo se necessário


def main(test_name: str, start_id: int = 0, end_id: int = None):
    # Conexão com o banco usando SQLAlchemy
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    # Tabela de prompts
    table_name = f"{test_name}_prompts"
    query = f"SELECT * FROM {table_name} ORDER BY shuffle_id;"

    with engine.connect() as conn:
        result = conn.execute(text(query))
        prompts_data = [dict(row) for row in result]

        # Filtra no Python pelo shuffle_id
        if start_id is not None:
            prompts_data = [row for row in prompts_data if row['shuffle_id'] >= start_id]
        if end_id is not None:
            prompts_data = [row for row in prompts_data if row['shuffle_id'] <= end_id]

        # Cria tabela de resultados se não existir
        results_table = f"{test_name}_results"
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {results_table} (
                id SERIAL PRIMARY KEY,
                search_title TEXT,
                shuffle_id INT,
                response TEXT
            );
        """))

    # Inicializa a LLM Groq
    groq_llm = LLM(
        model="llama-3.1-8b-instant",
        api_key_env="GROQ_API_KEY",
        endpoint="https://api.groq.com/openai/v1/chat/completions"
    )

    # Processa cada prompt e salva no banco
    with engine.begin() as conn:  # begin() garante commit automático
        for idx, row in enumerate(prompts_data, 1):
            prompt = row.get('prompt')
            search_title = row.get('search_title')
            shuffle_id = row.get('shuffle_id')

            try:
                response = groq_llm.generate(prompt)
                print(f"\nPrompt {idx} (shuffle_id={shuffle_id}): {prompt}")
                print(f"Resposta: {response}")

                # Insere no banco
                conn.execute(
                    text(f"INSERT INTO {results_table} (search_title, shuffle_id, response) VALUES (:search_title, :shuffle_id, :response)"),
                    {"search_title": search_title, "shuffle_id": shuffle_id, "response": response}
                )
            except Exception as e:
                print(f"Erro ao processar prompt {idx} (shuffle_id={shuffle_id}): {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processa prompts de um teste usando LLM")
    parser.add_argument("test_name", type=str, help="Nome do teste (prefixo da tabela de prompts)")
    parser.add_argument("--start_id", type=int, default=0, help="ID inicial do shuffle para processar")
    parser.add_argument("--end_id", type=int, default=None, help="ID final do shuffle para processar")
    args = parser.parse_args()

    main(args.test_name, args.start_id, args.end_id)
