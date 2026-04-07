import React from 'react';
import DiagramRenderer from './DiagramRenderer';

export default function ReportViewer({ scanData, aiAnalysis }) {
    return (
        <div className="report-viewer">
            <h2>Diagnóstico da Base de Dados & Laboratório</h2>

            <div className="telemetry-box">
                <h3>Dados de Telemetria Esgotados</h3>
                <p><strong>Alvo Base Isolado:</strong> {scanData?.target || "N/A"}</p>
                <p><strong>Status Laboratório:</strong> <span className={scanData?.status === 'up' ? 'status-up' : 'status-down'}>{scanData?.status || "Ausente"}</span></p>
                <div className="open-ports-logs">
                    <h4>Portas de Entrada Analisadas (Abertas):</h4>
                    <ul>
                        {scanData?.open_ports?.map((port, i) => (
                            <li key={i}>
                                Porta <code>{port.port}</code> / {port.protocol.toUpperCase()} — {port.name}
                                {port.product && <span> ({port.product} {port.version})</span>}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            <div className="ai-analysis-box">
                <h3>Insights da Camada Cognitiva (Google Gemini LLM)</h3>
                {!aiAnalysis?.vulnerabilidades || aiAnalysis.vulnerabilidades.length === 0 ? (
                    <p>Submeta a análise para gerar relatórios de anomalia.</p>
                ) : (
                    aiAnalysis.vulnerabilidades.map((vuln, index) => (
                        <div key={index} className="vuln-entry">
                            <h4 className="vuln-title">🔴 {vuln.titulo}</h4>

                            <div className="vuln-section text-block">
                                <h5>Prova Documentacional Causal:</h5>
                                {/* Renderiza as tags HTML enviadas pela IA com segurança */}
                                <div dangerouslySetInnerHTML={{ __html: vuln.explicacao }}></div>
                            </div>

                            <div className="vuln-section diagram-block">
                                <h5>Mapeamento do Exploit (Topologia de Fluxo):</h5>
                                <DiagramRenderer chartCode={vuln.mermaid} />
                            </div>

                            <div className="vuln-section code-block">
                                <h5>Solução / Patch Causal:</h5>
                                <pre><code>{vuln.patch}</code></pre>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
