import nmap
import ipaddress
import httpx
import json
import asyncio
import os
from typing import Dict, Any, List

class SecurityScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
    
    def _validate_ip(self, ip_str: str) -> bool:
        """
        Validação irrestrita de IP: Permite apenas IPs privados.
        Bloqueia totalmente o escaneamento de alvos externos/públicos.
        """
        allowed_hosts = ["localhost", "127.0.0.1", "host.docker.internal", "juice-shop"]
        if ip_str in allowed_hosts:
            return True
        try:
            ip = ipaddress.ip_address(ip_str)
            return ip.is_private or ip.is_loopback
        except ValueError:
            # Se for um hostname (ex: juice-shop), permite se for do laboratório
            return ip_str == "juice-shop"

    async def scan_target(self, target: str, port_range: str = "1-65535") -> Dict[str, Any]:
        """
        Executa um escaneamento nmap síncrono envolvido em uma thread assíncrona.
        Se target for localhost, tenta também host.docker.internal para alcançar o host do Docker.
        """
        clean_target = target
        if target == "localhost":
             # Dentro do Docker, localhost é o próprio container. 
             # Para o usuário testar "o que está no computador dele", usamos host.docker.internal
             clean_target = "host.docker.internal"
             print(f"[*] Traduzindo localhost para {clean_target} para alcançar o host Docker.")

        if not self._validate_ip(clean_target):
            raise ValueError(f"[ERRO DE SEGURANÇA] O alvo {target} ({clean_target}) não é um IP privado válido do laboratório. Execução bloqueada.")

        print(f"[*] Iniciando escaneamento Nmap no alvo isolado: {clean_target}:{port_range}")
        
        # Executa nmap em thread separada para não bloquear o event loop do FastAPI
        # Adicionamos -Pn porque alguns hosts locais podem não responder a ping
        scan_data = await asyncio.to_thread(self.nm.scan, clean_target, port_range, arguments="-sV -Pn -T4")
        
        results = {
            "target": target,
            "resolved_target": clean_target,
            "status": "up" if clean_target in self.nm.all_hosts() else "down",
            "open_ports": [],
            "http_metadata": {}
        }

        if clean_target in self.nm.all_hosts():
            for proto in self.nm[clean_target].all_protocols():
                ports = self.nm[clean_target][proto].keys()
                for port in sorted(ports):
                    port_info = self.nm[clean_target][proto][port]
                    if port_info['state'] == 'open':
                        results["open_ports"].append({
                            "port": port,
                            "protocol": proto,
                            "name": port_info.get('name', ''),
                            "product": port_info.get('product', ''),
                            "version": port_info.get('version', '')
                        })
                        
                        # Se for provável que seja HTTP/HTTPS, tenta um fingerprint HTTP
                        if port_info.get('name', '') in ['http', 'https', 'http-alt'] or port in [80, 443, 3000, 8000, 8080]:
                            http_info = await self._gather_http_metadata(clean_target, port, port_info.get('name', 'http'))
                            if http_info:
                                results["http_metadata"][f"{port}"] = http_info

        # Persistência do resultado bruto em arquivo local
        self._save_scan_results(results)
        return results

    async def _gather_http_metadata(self, target: str, port: int, service_name: str) -> Dict[str, Any]:
        """
        Coleta metadados HTTP assincronamente usando httpx.
        """
        # Ajusta target localhost para 127.0.0.1 se necessário para httpx ou usa como está
        host = "127.0.0.1" if target == "localhost" else target
        scheme = "https" if "https" in service_name else "http"
        url = f"{scheme}://{host}:{port}"
        
        print(f"[*] Coletando metadados HTTP em {url}...")
        
        metadata = {
            "url": url,
            "status_code": None,
            "headers": {},
            "server": None,
            "powered_by": None
        }
        
        async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
            try:
                response = await client.get(url)
                metadata["status_code"] = response.status_code
                metadata["headers"] = dict(response.headers)
                metadata["server"] = response.headers.get("server")
                metadata["powered_by"] = response.headers.get("x-powered-by")
            except Exception as e:
                metadata["error"] = str(e)
                
        return metadata

    def _save_scan_results(self, results: Dict[str, Any]):
        """
        Salva o resultado completo em scan_results.json
        """
        output_file = "scan_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"[*] Resultados salvos com sucesso em {os.path.abspath(output_file)}")

if __name__ == "__main__":
    scanner = SecurityScanner()
    asyncio.run(scanner.scan_target("localhost", "3000"))
