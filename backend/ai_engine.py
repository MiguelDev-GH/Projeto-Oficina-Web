import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
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
        
        raw_text = response.content.strip()
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

    async def analyze_file_target(self, file_data: str) -> dict:
        print(f"[*] Iniciando análise de código fonte (Tamanho: {len(file_data)} bytes)...")
        
        file_prompt_template = PromptTemplate(
            input_variables=["file_data"],
            template="""
Você é um Arquiteto de Software Especialista e Engenheiro de Segurança Principal (SecOps) Autônomo.
Realize uma Análise Estática de Código Fonte (SAST) no seguinte arquivo:

[CONTEÚDO DO ARQUIVO]
{file_data}

O seu foco principal deve ser em:
1. Análise de vulnerabilidades no código fonte.
2. Boas práticas de segurança.
3. Sugestões de correção.

Quais são as falhas essenciais, vulnerabilidades ou más práticas que você detecta neste código? Crie uma resposta de raciocínio profundo formatada da seguinte forma:
(a) Uma prova documental de como isso é explorável junto com uma explicação técnica profunda de por que o código gera o bug.
(b) Gere o código explícito da correção da vulnerabilidade (PATCH) pronto para aplicação.
(c) Crie uma estrutura visual para Mermaid.js que descreva explicitamente o caminho lógico da vulnerabilidade no código.

Retorne SOMENTE um JSON estruturado com os seguintes campos (sem crases Markdown, apenas o JSON cru):
{{
    "vulnerabilidades": [
        {{
            "titulo": "Nome da Falha",
            "explicacao": "Sua prova técnica (use tags HTML como <br> e <b> para formatar o texto e quebrar linhas)",
            "patch": "O código de correção cru",
            "mermaid": "graph TD\\nA[Identificacao] --> B[Analise]\\nB --> C[Conclusao]\\n(REGRA: Use apenas letras e espaços nos nós.)"
        }}
    ]
}}
"""
        )
        
        file_chain = file_prompt_template | self.llm
        
        print("[*] Enviando solicitação SAST para a IA Generativa (isso pode levar de 5 a 20 segundos)...")
        
        try:
            response = await file_chain.ainvoke({"file_data": file_data})
            print("[✓] Resposta da IA para arquivo recebida com sucesso!")
        except Exception as e:
            print(f"[ERRO] A IA falhou ao processar a análise de arquivo: {str(e)}")
            return {"error": str(e), "status": "ai_failure"}
        
        raw_text = response.content.strip()
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
            print(f"[ERRO] Falha ao analisar JSON da IA (Arquivo): {e}")
            return {"error": "A IA não retornou um JSON válido.", "raw": raw_text}

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    engine = PentestAIEngine()
    result = asyncio.run(engine.analyze_scan())
    print(json.dumps(result, indent=2))