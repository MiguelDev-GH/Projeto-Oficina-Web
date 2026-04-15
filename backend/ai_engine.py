import os
import json
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import asyncio

# Load .env at module level to ensure variables are available
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

class PentestAIEngine:
    def __init__(self, model_name: str = None):
        # LangChain Google GenAI uses GOOGLE_API_KEY by default
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if not api_key or api_key == "sua_chave_aqui":
            raise ValueError("[CRITICAL ERROR] GOOGLE_API_KEY not found or invalid in .env file. Please add your real Gemini API key.")
        
        # Ensure the environment variable is set for the library's internal use as well
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Determine model: explicit argument > env var > default
        if model_name:
            chosen_model = model_name
        else:
            chosen_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        print(f"[*] Conectando ao provedor de IA com o modelo {chosen_model}...")
        self.llm = ChatGoogleGenerativeAI(
            model=chosen_model,
            temperature=0.2,
            api_key=api_key,
            max_retries=2
        )
        
        # ── Prompt modo INFRA (Nmap) ──────────────────────────────────────────
        self.prompt_template = PromptTemplate(
            input_variables=["scan_data"],
            template="""
Você é um Arquiteto de Software Especialista e Engenheiro de Segurança Principal (SecOps) Autônomo.
Analise o seguinte resultado de varredura (scan) de um ambiente isolado:

[DADOS DO SCAN EM JSON]
{scan_data}

Quais são as falhas essenciais ou vulnerabilidades que você detecta nos serviços e portas abertas? Crie uma resposta de raciocínio profundo formatada da seguinte forma:
(a) Uma prova documental de como isso é explorável junto com uma explicação técnica profunda de por que o código gera o bug.
(b) Gere o código explícito da correção da vulnerabilidade (PATCH) pronto para aplicação.
(c) Crie uma estrutura visual para Mermaid.js que descreva explicitamente o caminho lógico da detecção.

Retorne SOMENTE um JSON estruturado com os seguintes campos (sem crases Markdown, apenas o JSON cru):
{{
    "vulnerabilidades": [
        {{
            "titulo": "Nome da Falha",
            "explicacao": "Sua prova técnica (use tags HTML como <br> e <b> para formatar o texto e quebrar linhas)",
            "patch": "O código de correção cru",
            "mermaid": "graph TD\\nA[Identificacao] --> B[Analise]\\nB --> C[Conclusao]\\n(REGRA: Use apenas letras e espaços nos nós. Ex: A[Busca de Portas] --> B[Vulnerabilidade Detectada].)"
        }}
    ]
}}
"""
        )
        self.chain = self.prompt_template | self.llm

    # ─────────────────────────────────────────────────────────────────────────
    # MODO INFRA: análise de scan Nmap
    # ─────────────────────────────────────────────────────────────────────────
    async def analyze_scan(self) -> dict:
        try:
            with open("scan_results.json", "r", encoding="utf-8") as f:
                scan_data_str = f.read()
        except FileNotFoundError:
            return {"error": "Arquivo scan_results.json não encontrado. Execute o scanner primeiro."}
            
        print(f"[*] Iniciando análise de dados (Tamanho: {len(scan_data_str)} bytes)...")
        print("[*] Enviando solicitação para a IA Generativa (isso pode levar de 5 a 20 segundos)...")
        
        try:
            response = await self.chain.ainvoke({"scan_data": scan_data_str})
            print("[✓] Resposta da IA recebida com sucesso!")
        except Exception as e:
            print(f"[ERRO] A IA falhou ao processar a solicitação: {str(e)}")
            return {"error": str(e), "status": "ai_failure"}
        
        return self._parse_json_response(response.content)

    # ─────────────────────────────────────────────────────────────────────────
    # MODO WEB: análise DAST multimodal (HTML + Screenshot + Console Logs)
    # ─────────────────────────────────────────────────────────────────────────
    async def analyze_web_target(self, web_data: dict) -> dict:
        """
        Análise multimodal: envia ao Gemini o HTML renderizado, o screenshot
        (imagem JPEG em Base64) e os logs do console da página alvo.
        Retorna JSON com fingerprint de IA, riscos de injeção e riscos de console.
        """
        url = web_data.get("url", "N/A")
        html_snippet = web_data.get("html", "")[:12000]   # Limite para não estourar o contexto
        screenshot_b64 = web_data.get("screenshot_b64", "")
        console_logs = web_data.get("console_logs", [])
        network_errors = web_data.get("network_errors", [])

        # Formata logs do console em texto legível
        console_text = "\n".join(
            f"[{log['type'].upper()}] {log['text']}  @ {log.get('location', '')}"
            for log in console_logs
        ) or "Nenhum log de console capturado."

        network_text = "\n".join(
            f"[FALHA REDE] {e['method']} {e['url']} → {e['failure']}"
            for e in network_errors
        ) or "Nenhum erro de rede."

        prompt_text = f"""Você é um Engenheiro de Segurança Ofensiva (Red Team) e especialista em análise de aplicações web.
Analise a aplicação web em: {url}

Você recebeu três fontes de dados:
1. **HTML RENDERIZADO** (DOM pós-execução de JavaScript, primeiros 12000 chars):
```html
{html_snippet}
```

2. **LOGS DO CONSOLE DO NAVEGADOR** (capturados durante o carregamento):
```
{console_text}
```

3. **ERROS DE REDE** (requisições que falharam):
```
{network_text}
```

4. **SCREENSHOT** da página (imagem anexada à esta mensagem).

Realize uma análise DAST (Dynamic Application Security Testing) completa e retorne SOMENTE um JSON cru (sem crases Markdown) com esta estrutura exata:
{{
    "fingerprint_ia": {{
        "detectado": true ou false,
        "confianca": "alta/media/baixa",
        "evidencias": ["evidência 1", "evidência 2"],
        "explicacao": "Explicação de por que esta página parece (ou não) gerada por ferramentas automáticas/IA. Use tags HTML <br> e <b>."
    }},
    "web_vulnerabilidades": [
        {{
            "titulo": "Nome da Vulnerabilidade",
            "categoria": "SQLi | XSS | CSRF | IDOR | InfoDisclosure | MiscConfig | Outro",
            "severidade": "Crítica | Alta | Média | Baixa | Informação",
            "explicacao": "Prova técnica detalhada com referência ao DOM/HTML. Use tags HTML <br> e <b>.",
            "evidencia_dom": "Trecho de código HTML ou padrão que prova a vulnerabilidade",
            "patch": "Código de correção cru ou recomendação técnica",
            "mermaid": "graph TD\\nA[Atacante] --> B[Explora Input]\\nB --> C[Injecao SQL]"
        }}
    ],
    "riscos_console": [
        {{
            "titulo": "Nome do Risco",
            "tipo": "vazamento_dados | erro_arquitetura | dependencia_vulneravel | Outro",
            "severidade": "Alta | Média | Baixa",
            "log_original": "Log exato capturado",
            "explicacao": "Por que este log representa um risco de segurança."
        }}
    ],
    "resumo_executivo": "Parágrafo resumindo os principais riscos encontrados na análise. Use tags HTML <br> e <b>."
}}"""

        print(f"[*] Iniciando análise multimodal DAST para {url}...")
        print(f"[*] Contexto: {len(html_snippet)} chars HTML, {len(console_logs)} console logs, screenshot={bool(screenshot_b64)}")

        # ── Monta mensagem multimodal (texto + imagem) ────────────────────────
        content_parts = [{"type": "text", "text": prompt_text}]

        if screenshot_b64:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"},
            })

        message = HumanMessage(content=content_parts)

        try:
            response = await self.llm.ainvoke([message])
            print("[✓] Resposta multimodal da IA recebida com sucesso!")
        except Exception as e:
            print(f"[ERRO] Análise multimodal falhou: {str(e)}")
            return {"error": str(e), "status": "ai_failure"}

        parsed = self._parse_json_response(response.content)
        self._save_analysis(parsed)
        return parsed

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _parse_json_response(self, raw_content: str) -> dict:
        raw_text = raw_content.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        try:
            parsed_data = json.loads(raw_text)
            self._save_analysis(parsed_data)
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"[ERRO] Falha ao analisar JSON da IA: {e}")
            return {"error": "A IA não retornou um JSON válido.", "raw": raw_text}

    def _save_analysis(self, data: dict):
        with open("analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("[*] Análise salva em analysis_results.json")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    engine = PentestAIEngine()
    result = asyncio.run(engine.analyze_scan())
    print(json.dumps(result, indent=2))