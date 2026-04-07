# Plano de Fase 1: Fundação Primária

**Status**: Concluído
**Data**: 2026-04-07

## Resumo das Ações Realizadas

1. **Estrutura de Pastas**:
   - Criação das pastas raiz `frontend/`, `backend/` e `docs/`.

2. **Dependências do Backend (`backend/requirements.txt`)**:
   - Foram listadas todas as dependências exigidas (fastapi, uvicorn, python-nmap, httpx, langchain, langchain-google-genai, jinja2, weasyprint).

3. **Backend Base (`backend/main.py`)**:
   - Inicializada a instância do FastAPI com Uvicorn ASGI.
   - Criada a rota de saúde `/` que retorna um Hello World encapsulado para teste da infraestrutura.

4. **Laboratório Isolado (`docker-compose.yml`)**:
   - Configurado o contêiner vulnerável `bkimminich/juice-shop` exposto na porta restrita `3000`.
   - Adicionado um serviço para o próprio backend, conectando ambos em uma sub-rede bridge privada (`secops_net`), preparando a topologia de exploração segura simulada 172.x.
   - Adicionada configuração de segurança `no-new-privileges` no laboratório para conter os impactos dos testes.

## Próximos Passos (Fase 2)
Avançar para a implementação da varredura restritiva com `python-nmap` e verificação de redes (`ipaddress.is_private`) visando o escaneamento ativo no Juice Shop.
