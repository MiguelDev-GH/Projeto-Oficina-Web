"""
web_scraper.py — WebReconScanner
Usa Playwright headless (Chromium) para capturar:
  - HTML renderizado completo (DOM pós-JS)
  - Screenshot da página em Base64
  - Todos os logs do console (console.log, console.error, warnings, erros de rede)
"""

import asyncio
import base64
import json
import os
from typing import Any, Dict, List

from playwright.async_api import async_playwright, ConsoleMessage, Request, Response


class WebReconScanner:
    """
    Scanner DAST headless. Captura artefatos de uma URL para análise multimodal por IA.
    """

    async def scan_url(self, url: str) -> Dict[str, Any]:
        """
        Executa a captura completa da URL fornecida.
        Retorna um dict com: url, html, screenshot_b64, console_logs, network_errors.
        """
        print(f"[*] WebReconScanner: iniciando captura headless em {url}")

        console_logs: List[Dict[str, str]] = []
        network_errors: List[Dict[str, str]] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                ignore_https_errors=True,
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36 SecOps-DAST/1.0"
                ),
            )
            page = await context.new_page()

            # ── Captura de Console Logs ──────────────────────────────────────────
            def on_console(msg: ConsoleMessage):
                console_logs.append(
                    {
                        "type": msg.type,   # log | warning | error | info | debug
                        "text": msg.text,
                        "location": f"{msg.location.get('url', '')}:{msg.location.get('lineNumber', '')}",
                    }
                )

            page.on("console", on_console)

            # ── Captura de Erros de Página (JS não capturado) ───────────────────
            def on_page_error(exc):
                console_logs.append(
                    {"type": "pageerror", "text": str(exc), "location": url}
                )

            page.on("pageerror", on_page_error)

            # ── Captura de Erros de Rede ─────────────────────────────────────────
            def on_request_failed(request: Request):
                network_errors.append(
                    {
                        "type": "network_fail",
                        "url": request.url,
                        "method": request.method,
                        "failure": request.failure or "unknown",
                    }
                )

            page.on("requestfailed", on_request_failed)

            # ── Navegação ────────────────────────────────────────────────────────
            try:
                await page.goto(url, wait_until="networkidle", timeout=30_000)
            except Exception as e:
                print(f"[!] Timeout/erro na navegação, capturando mesmo assim: {e}")
                # Capturamos o que conseguimos mesmo com timeout

            # ── HTML Renderizado ─────────────────────────────────────────────────
            html_content = await page.content()

            # ── Screenshot em Base64 ─────────────────────────────────────────────
            screenshot_bytes = await page.screenshot(
                type="jpeg",
                quality=75,
                full_page=False,   # viewport apenas para o PDF ficar gerenciável
            )
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            await browser.close()

        result = {
            "url": url,
            "mode": "web",
            "html": html_content,
            "screenshot_b64": screenshot_b64,
            "console_logs": console_logs,
            "network_errors": network_errors,
            "html_size_bytes": len(html_content.encode("utf-8")),
            "console_log_count": len(console_logs),
        }

        # Persistência local (espelhar o padrão do scanner.py)
        self._save_results(result)

        print(
            f"[✓] Captura concluída: {len(html_content)} chars HTML, "
            f"{len(screenshot_bytes)} bytes screenshot, "
            f"{len(console_logs)} log(s) de console"
        )
        return result

    def _save_results(self, data: Dict[str, Any]):
        """Persiste os resultados (sem o screenshot para não poluir o JSON)."""
        output_file = "web_scan_results.json"
        slim = {k: v for k, v in data.items() if k != "screenshot_b64" and k != "html"}
        slim["html_preview"] = data["html"][:2000] + "… [truncado]"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(slim, f, indent=4, ensure_ascii=False)
        print(f"[*] Resultado resumido salvo em {os.path.abspath(output_file)}")


if __name__ == "__main__":
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else "http://juice-shop:3000"
    result = asyncio.run(WebReconScanner().scan_url(url))
    print(f"Screenshot size: {len(result['screenshot_b64'])} chars (Base64)")
    print(f"Console logs: {result['console_logs']}")
