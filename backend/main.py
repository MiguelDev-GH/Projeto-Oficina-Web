from fastapi import FastAPI, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from scanner import SecurityScanner
from ai_engine import PentestAIEngine
from report_generator import ReportGenerator
import json
import os
import hashlib
import asyncio
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


@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...), model: str = Form(...)):
    """
    MODO ARQUIVO: Consulta VirusTotal + análise inteligente via Gemini.
    """
    try:
        contents = await file.read()
        file_size = len(contents)
        print(f"[*] Arquivo recebido: {file.filename} ({file_size} bytes)")

        # Calcula SHA-256 do arquivo
        sha256 = hashlib.sha256(contents).hexdigest()
        print(f"[*] SHA-256: {sha256}")

        vt_api_key = os.getenv("VIRUSTOTAL_API_KEY", "")
        if not vt_api_key:
            return {"status": "erro_interno", "error": "VIRUSTOTAL_API_KEY não configurada no .env"}

        vt_headers = {"x-apikey": vt_api_key}
        vt_data = None

        import httpx

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Consulta por hash no VirusTotal
            print(f"[*] Consultando VirusTotal por hash...")
            vt_resp = await client.get(
                f"https://www.virustotal.com/api/v3/files/{sha256}",
                headers=vt_headers
            )

            if vt_resp.status_code == 200:
                vt_data = vt_resp.json().get("data", {})
                print(f"[✓] Arquivo encontrado no VirusTotal (hash conhecido)")

            elif vt_resp.status_code == 404:
                # Arquivo desconhecido — faz upload ao VirusTotal
                print(f"[*] Hash não encontrado. Enviando arquivo ao VirusTotal...")
                upload_resp = await client.post(
                    "https://www.virustotal.com/api/v3/files",
                    headers=vt_headers,
                    files={"file": (file.filename, contents)}
                )

                if upload_resp.status_code not in (200, 201):
                    return {"status": "erro_interno", "error": f"Falha no upload ao VirusTotal: {upload_resp.text}"}

                analysis_id = upload_resp.json().get("data", {}).get("id", "")
                print(f"[*] Upload aceito. Análise ID: {analysis_id}")

                # Polling até a análise terminar (máx 120s)
                for attempt in range(12):
                    await asyncio.sleep(10)
                    print(f"[*] Polling análise... tentativa {attempt + 1}/12")
                    poll_resp = await client.get(
                        f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                        headers=vt_headers
                    )
                    if poll_resp.status_code == 200:
                        poll_data = poll_resp.json().get("data", {})
                        if poll_data.get("attributes", {}).get("status") == "completed":
                            # Busca o relatório completo do arquivo
                            file_resp = await client.get(
                                f"https://www.virustotal.com/api/v3/files/{sha256}",
                                headers=vt_headers
                            )
                            if file_resp.status_code == 200:
                                vt_data = file_resp.json().get("data", {})
                            else:
                                vt_data = poll_data
                            print(f"[✓] Análise VirusTotal concluída!")
                            break
                else:
                    return {"status": "erro_interno", "error": "Timeout: análise do VirusTotal não concluiu em 60s. Tente novamente."}

            else:
                return {"status": "erro_interno", "error": f"Erro na API do VirusTotal: {vt_resp.status_code} — {vt_resp.text}"}

        if not vt_data:
            return {"status": "erro_interno", "error": "Não foi possível obter dados do VirusTotal."}

        # Extrai resumo para scan_data
        vt_attrs = vt_data.get("attributes", {})
        vt_stats = vt_attrs.get("last_analysis_stats", {})
        scan_data_summary = {
            "tipo": "VIRUSTOTAL",
            "sha256": sha256,
            "tamanho_bytes": file_size,
            "tipo_mime": vt_attrs.get("type_description", "N/A"),
            "stats": vt_stats,
            "nomes_populares": vt_attrs.get("popular_threat_classification", {}),
            "reputacao": vt_attrs.get("reputation", "N/A")
        }

        print(f"[*] Stats VT: {vt_stats}")
        print(f"[*] Enviando dados do VirusTotal para análise Gemini com modelo {model}...")

        # Alimenta o Gemini com o JSON do VirusTotal
        engine = PentestAIEngine(model_name=model)
        ai_analysis = await engine.analyze_file_target(vt_data, file.filename)

        pdf_url = None
        if "error" not in ai_analysis:
            report_gen = ReportGenerator()
            scan_mock = {
                "scan_id": "vt_scan",
                "timestamp": vt_attrs.get("last_analysis_date", "N/A"),
                "target": f"Arquivo: {file.filename} (SHA-256: {sha256})",
                "open_ports": [],
                "nmap_raw": f"Análise VirusTotal — {file.filename} — Detecções: {vt_stats.get('malicious', 0)} maliciosas"
            }
            report_gen.generate_pdf(scan_mock, ai_analysis)
            pdf_url = "/reports/secops_report.pdf"

        return {
            "status": "sucesso",
            "alvo": file.filename,
            "scan_data": scan_data_summary,
            "inteligencia": ai_analysis,
            "pdf_report": pdf_url
        }

    except Exception as e:
        print(f"[ERRO CRÍTICO ARQUIVO/VT] {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "erro_interno", "error": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)