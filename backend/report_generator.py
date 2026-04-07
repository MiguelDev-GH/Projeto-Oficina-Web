import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

class ReportGenerator:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.output_dir = os.path.join(os.path.dirname(__file__), "reports")
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def generate_pdf(self, scan_data: dict, analysis_data: dict) -> str:
        print("[*] Rendering SEC-OPS report template...") # Translated output to English
        template = self.env.get_template("report.html.j2")
        
        html_content = template.render(
            scan=scan_data,
            anomalias=analysis_data.get("vulnerabilidades", [])
        )
        
        output_file = os.path.join(self.output_dir, "secops_report.pdf")
        
        print("[*] Converting to professional PDF...") # Translated output to English
        HTML(string=html_content).write_pdf(output_file)
        
        print(f"[*] Report finalized and saved to: {output_file}") # Translated output to English
        return output_file