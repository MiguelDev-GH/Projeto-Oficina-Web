import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

class ReportGenerator:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.output_dir = os.path.join(os.path.dirname(__file__), "reports")
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    # ── Modo Infra (Nmap) ────────────────────────────────────────────────────
    def generate_pdf(self, scan_data: dict, analysis_data: dict) -> str:
        print("[*] Renderizando o template do relatório SEC-OPS (Infra)...")
        template = self.env.get_template("report.html.j2")
        
        html_content = template.render(
            scan=scan_data,
            anomalias=analysis_data.get("vulnerabilidades", [])
        )
        
        output_file = os.path.join(self.output_dir, "secops_report.pdf")
        
        print("[*] Convertendo para PDF profissional via WeasyPrint...")
        HTML(string=html_content).write_pdf(output_file)
        
        print(f"[*] Relatório finalizado e salvo em: {output_file}")
        return output_file

    # ── Modo Web (DAST Multimodal) ───────────────────────────────────────────
    def generate_web_pdf(self, web_data: dict, analysis_data: dict) -> str:
        print("[*] Renderizando o template do relatório SEC-OPS (Web DAST)...")
        template = self.env.get_template("report_web.html.j2")

        html_content = template.render(
            scan=web_data,
            fingerprint=analysis_data.get("fingerprint_ia", {}),
            web_vulns=analysis_data.get("web_vulnerabilidades", []),
            console_risks=analysis_data.get("riscos_console", []),
            resumo=analysis_data.get("resumo_executivo", ""),
        )

        output_file = os.path.join(self.output_dir, "secops_web_report.pdf")

        print("[*] Convertendo relatório Web DAST para PDF via WeasyPrint...")
        HTML(string=html_content).write_pdf(output_file)

        print(f"[*] Relatório Web finalizado e salvo em: {output_file}")
        return output_file