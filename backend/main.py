from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows React frontend requests (localhost:5173 etc)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World. Isolated FastAPI environment running successfully."}

@app.post("/analyze")
async def analyze_target(target: str = "172.17.0.2"):
    """
    Orchestrates the 3 phases in a single call.
    Attention: The scanner actively blocks any public IP.
    """
    try:
        scanner = SecurityScanner()
        scan_results = await scanner.scan_target(target, "3000,80,443")
        
        engine = PentestAIEngine()
        ai_analysis = await engine.analyze_scan()
        
        if "error" not in ai_analysis:
            report_gen = ReportGenerator()
            pdf_path = report_gen.generate_pdf(scan_results, ai_analysis)
        else:
            pdf_path = None
            
        return {
            "status": "sucesso",
            "alvo": target,
            "scan_data": scan_results,
            "inteligencia": ai_analysis,
            "pdf_report": pdf_path
        }
        
    except ValueError as ve:
        return {"status": "bloqueado", "error": str(ve)}
    except Exception as e:
        return {"status": "erro_interno", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)