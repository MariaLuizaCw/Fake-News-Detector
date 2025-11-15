from typing import List, Dict

def load_credible_domains(file_path: str) -> List[str]:
    """Carrega domínios confiáveis de um arquivo de texto (uma linha por domínio)."""
    with open(file_path, "r", encoding="utf-8") as f:
        domains = [line.strip() for line in f if line.strip()]
    return domains