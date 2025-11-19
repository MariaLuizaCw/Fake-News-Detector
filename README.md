# Fake News Detection Tests

Repositório com testes de detecção de fake news usando RAG e diferentes prompts.

Repositório com testes de detecção de fake news usando RAG e diferentes prompts.

| Teste  | Fonte       | RAG | Iterações | Resultados por Iteração | Title Refiner | Pré-filtro Embedding                     | Prompt de Classificação                |
|--------|------------|-----|-----------|------------------------|---------------|-----------------------------------------|--------------------------------------|
| Test1  | DuckDuckGo | Sim | 2         | 10                     | Sim           | sentence-transformers/all-MiniLM-L6-v2 | real / fake                           |
| Test2  | DuckDuckGo | Sim | 2         | 10                     | Sim           | sentence-transformers/all-MiniLM-L6-v2 | real / fake / real with misinformation |
| Test3  | N/A        | Não | N/A       | N/A                    | Não           | N/A                                     | real / fake                           |
| Test4  | Google     | Sim | 1         | 10                     | Sim           | sentence-transformers/all-MiniLM-L6-v2 | real / fake                           |

**Observações:**
- **Title Refiner:** módulo que refina e melhora os títulos recuperados antes de enviar ao modelo, aumentando a qualidade da classificação.  
- **Número de Iterações:** indica quantas vezes a busca externa é realizada; ex.: 2 iterações = primeira busca de 10 resultados + segunda busca de mais 10 resultados.  
- **Resultados por Iteração:** quantidade de resultados coletados em cada iteração de busca.  
- RAG = Retrieval-Augmented Generation, técnica que combina recuperação de dados externos com geração de respostas.