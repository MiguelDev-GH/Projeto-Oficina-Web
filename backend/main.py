from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from scanner import SecurityScanner
from ai_engine import PentestAIEngine
from report_generator import ReportGenerator
import json
import os
from dotenv import load_dotenv

# Ensure we load the .env file from the same directory as main.py
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

app = FastAPI(title="SecOps AI Pentester", version="2.0.0")

# Garante que a pasta reports existe para montagem estática
reports_path = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(reports_path, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows React frontend requests (localhost:5173 etc)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta a pasta de relatórios como arquivos estáticos para acesso via browser
app.mount("/reports", StaticFiles(directory=reports_path), name="reports")


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────
class WebAnalyzeRequest(BaseModel):
    target_url: str
    model: str = "gemini-2.5-flash"


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "SecOps AI Pentester v2 — Endpoints: /analyze (infra) | /analyze-web (DAST)"}


@app.post("/analyze")
async def analyze_target(target: str = "172.17.0.2", model: str = None):
    """
    MODO INFRAESTRUTURA: Orquestra scan Nmap + análise de IA textual.
    Atenção: O scanner bloqueia ativamente qualquer IP público.
    """
    try:
        # Extração de porta se houver (ex: localhost:3000)
        port_to_scan = "3000,80,443,8000,8080"
        clean_target = target
        
        if ":" in target:
            clean_target, specific_port = target.split(":")
            port_to_scan = specific_port
            print(f"[*] Alvo detectado com porta específica: {clean_target} na porta {specific_port}")

        scanner = SecurityScanner()
        scan_results = await scanner.scan_target(clean_target, port_to_scan)
        
        engine = PentestAIEngine(model_name=model)
        ai_analysis = await engine.analyze_scan()
        
        pdf_url = None
        if "error" not in ai_analysis:
            report_gen = ReportGenerator()
            report_gen.generate_pdf(scan_results, ai_analysis)
            pdf_url = "/reports/secops_report.pdf"
            
        return {
            "status": "sucesso",
            "alvo": target,
            "scan_data": scan_results,
            "inteligencia": ai_analysis,
            "pdf_report": pdf_url
        }
        
    except ValueError as ve:
        return {"status": "bloqueado", "error": str(ve)}
    except Exception as e:
        print(f"[ERRO CRÍTICO NO BACKEND] {str(e)}")
        return {"status": "erro_interno", "error": str(e)}


@app.post("/analyze-web")
async def analyze_web(request: WebAnalyzeRequest):
    """
    MODO DAST MULTIMODAL: Orquestra captura Playwright (HTML + Screenshot + Console Logs)
    e análise multimodal via Gemini (texto + imagem).
    """
    try:
        from web_scraper import WebReconScanner                   # import local para não falhar se playwright não estiver instalado em dev

        print(f"[*] Iniciando análise DAST Web em: {request.target_url}")

        # Fase 1: Captura headless
        scraper = WebReconScanner()
        web_data = await scraper.scan_url(request.target_url)

        # Fase 2: Análise multimodal por IA
        engine = PentestAIEngine(model_name=request.model)
        ai_analysis = await engine.analyze_web_target(web_data)

        # Fase 3: Geração de PDF
        pdf_url = None
        if "error" not in ai_analysis:
            report_gen = ReportGenerator()
            report_gen.generate_web_pdf(web_data, ai_analysis)
            pdf_url = "/reports/secops_web_report.pdf"

        # Remove screenshot do payload JSON de resposta para não sobrecarregar o frontend
        # O frontend recebe a URL do PDF que já contém a imagem
        web_data_slim = {k: v for k, v in web_data.items() if k != "screenshot_b64" and k != "html"}
        web_data_slim["screenshot_available"] = bool(web_data.get("screenshot_b64"))

        return {
            "status": "sucesso",
            "alvo": request.target_url,
            "scan_data": web_data_slim,
            "inteligencia": ai_analysis,
            "pdf_report": pdf_url
        }

    except Exception as e:
        print(f"[ERRO CRÍTICO NO BACKEND - DAST] {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "erro_interno", "error": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)