from fastapi import FastAPI, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

app = FastAPI(title="SecOps AI Pentester", version="1.0.0")

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

@app.get("/")
async def root():
    return {"message": "Olá Mundo. Ambiente FastAPI isolado rodando com sucesso."}

@app.post("/analyze")
async def analyze_target(target: str = "172.17.0.2", model: str = None):
    """
    Orchestrates the 3 phases in a single call.
    Attention: The scanner actively blocks any public IP.
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
            # O gerador salva o arquivo, nós retornamos apenas o nome para construir a URL
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

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...), model: str = Form(...)):
    """
    Endpoint para análise estática de código fonte (SAST).
    Recebe um arquivo em memória, valida e envia para a IA.
    """
    try:
        # Segurança: Validação de extensão
        allowed_extensions = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".html", ".css", ".txt"}
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in allowed_extensions:
            return {"status": "bloqueado", "error": f"Extensão de arquivo não permitida: {ext}"}

        # Segurança: Lendo e validando o tamanho na memória (Max 2MB)
        MAX_SIZE = 2 * 1024 * 1024 # 2MB
        contents = await file.read()
        if len(contents) > MAX_SIZE:
            return {"status": "bloqueado", "error": "Arquivo excede o limite de segurança de 2MB."}

        # Decodificar para string UTF-8
        try:
            file_data = contents.decode("utf-8")
        except UnicodeDecodeError:
            return {"status": "bloqueado", "error": "Falha na decodificação. O arquivo deve ser um texto válido em UTF-8."}
        
        print(f"[*] Analisando arquivo: {file.filename} ({len(contents)} bytes) usando {model}")

        # Iniciar a engine de IA para análise do arquivo
        engine = PentestAIEngine(model_name=model)
        ai_analysis = await engine.analyze_file_target(file_data)
        
        pdf_url = None
        if "error" not in ai_analysis:
            report_gen = ReportGenerator()
            
            # Formato simulado de scan para compatibilidade com o relatório
            scan_mock = {
                "scan_id": "sast_scan_01",
                "timestamp": "N/A",
                "target": f"Arquivo: {file.filename}",
                "open_ports": [],
                "nmap_raw": f"Análise estática de código fonte (SAST) do arquivo {file.filename}"
            }
            report_gen.generate_pdf(scan_mock, ai_analysis)
            pdf_url = "/reports/secops_report.pdf"
            
        return {
            "status": "sucesso",
            "alvo": file.filename,
            "scan_data": {"tipo": "SAST", "tamanho": len(contents)},
            "inteligencia": ai_analysis,
            "pdf_report": pdf_url
        }

    except Exception as e:
        print(f"[ERRO CRÍTICO SAST] {str(e)}")
        return {"status": "erro_interno", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)