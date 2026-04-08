import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import asyncio

class PentestAIEngine:
    def __init__(self, model_name: str = None):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("[CRITICAL ERROR] GEMINI_API_KEY or GOOGLE_API_KEY not found. Configure it in the .env file or environment variables.")
        
        # Determine model: explicit argument > env var > default
        if model_name:
            chosen_model = model_name
        else:
            chosen_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        print(f"[*] Connecting to AI provider with model {chosen_model}...")
        self.llm = ChatGoogleGenerativeAI(
            model=chosen_model,
            temperature=0.2,
            google_api_key=api_key,
            max_retries=2
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["scan_data"],
            template="""
You are an Autonomous Expert Software Architect and Principal Security Engineer (SecOps).
Analyze the following scan result from an isolated environment:

[SCAN DATA IN JSON]
{scan_data}

What are the essential flaws or vulnerabilities that you commonly detect underlying critical code and open ports in these scanned documents that you read from this scan? Create in your deep reasoning response actively formatted:
(a) A documentary proof of how this is exploitable along with a highly technical deep explanation providing why the code under analysis generates the bug.
(b) Generate in real-time the script coding actively writing the explicit logical correction of the vulnerability in complete isolated code containing the actual "patches" ready for active applications under the exploited infrastructure eliminating interventionist dependency on providers.
(c) Create without intervening in errors a visual and documentary structure of the dynamic block in textual outputs formatted for exclusive branching oriented to use in Mermaid.js code forging the descriptive scope so that the framework can create the diagram that explicitly describes visually on the screen the entire route that your logic found explicitly detailing each logical pathway to illustrate the exact dynamics and paths in detection of these vulnerabilities by the system in a step-by-step flow and detection by your AI.

Retorne SOMENTE um JSON estruturado com os seguintes campos (sem crases Markdown, apenas o JSON cru):
{{
    "vulnerabilidades": [
        {{
            "titulo": "Nome da Falha",
            "explicacao": "Sua prova documentacional e técnica (use tags HTML como <br> e <b> para formatar o texto e quebrar linhas visualmente)",
            "patch": "O código de correção cru",
            "mermaid": "graph TD\\nA[Inicio]-->B[Detectado]\\n (REGRA CRÍTICA DO MERMAID: É ESTRITAMENTE PROIBIDO usar parênteses (), aspas, chaves, colchetes ou caracteres especiais no texto dos nós. Use APENAS letras, números e espaços. O formato obrigatório é ID[Texto do No].)"
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
            return {"error": "File scan_results.json not found. Run the scanner first."}
            
        print(f"[*] Starting inference data analysis (Size: {len(scan_data_str)} bytes)...")
        print("[*] Sending request to generative AI (this may take 5 to 20 seconds)...")
        
        try:
            response = await self.chain.ainvoke({"scan_data": scan_data_str})
            print("[✓] AI response received successfully!")
        except Exception as e:
            print(f"[ERROR] AI failed to process the request: {str(e)}")
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
            print(f"[ERROR] Failed to parse JSON: {e}")
            return {"error": "AI did not return a valid JSON.", "raw": raw_text}

    def _save_analysis(self, data: dict):
        with open("analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("[*] Analysis saved to analysis_results.json")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    engine = PentestAIEngine()
    result = asyncio.run(engine.analyze_scan())
    print(json.dumps(result, indent=2))