import React from 'react';
import DiagramRenderer from './DiagramRenderer';

// ── Helpers ──────────────────────────────────────────────────────────────────
function severityClass(sev = '') {
    const s = sev.toLowerCase();
    if (s.includes('crítica') || s.includes('critica')) return 'sev-critica';
    if (s.includes('alta'))   return 'sev-alta';
    if (s.includes('média') || s.includes('media')) return 'sev-media';
    if (s.includes('baixa'))  return 'sev-baixa';
    return 'sev-info';
}

// ── Sub-componente: Modo Infra ────────────────────────────────────────────────
function InfraReport({ scanData, aiAnalysis }) {
    return (
        <>
            <div className="telemetry-box">
                <h3>Dados de Telemetria Esgotados</h3>
                <p><strong>Alvo Base Isolado:</strong> {scanData?.target || 'N/A'}</p>
                <p>
                    <strong>Status Laboratório:</strong>{' '}
                    <span className={scanData?.status === 'up' ? 'status-up' : 'status-down'}>
                        {scanData?.status || 'Ausente'}
                    </span>
                </p>
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
                                <div dangerouslySetInnerHTML={{ __html: vuln.explicacao }} />
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
        </>
    );
}

// ── Sub-componente: Modo Web ──────────────────────────────────────────────────
function WebReport({ scanData, aiAnalysis }) {
    const fingerprint = aiAnalysis?.fingerprint_ia || null;
    const webVulns    = aiAnalysis?.web_vulnerabilidades || [];
    const risks       = aiAnalysis?.riscos_console || [];
    const resumo      = aiAnalysis?.resumo_executivo || '';
    const consoleLogs = scanData?.console_logs || [];

    return (
        <>
            {/* Screenshot — disponível apenas no PDF (removido do JSON para não sobrecarregar) */}
            {scanData?.screenshot_available && (
                <div className="web-screenshot-section">
                    <h3>📸 Screenshot da Aplicação</h3>
                    <div style={{
                        background: '#18181b',
                        border: '1px solid #27272a',
                        borderRadius: '10px',
                        padding: '16px 20px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        color: '#a1a1aa',
                        fontSize: '0.9rem'
                    }}>
                        <span style={{ fontSize: '1.4rem' }}>🖼️</span>
                        <span>Screenshot capturado com sucesso.{' '}
                            <strong style={{ color: '#818cf8' }}>
                                Visualize no PDF completo
                            </strong>{' '}para ver a imagem renderizada da aplicação.
                        </span>
                    </div>
                </div>
            )}


            {/* Meta-dados da captura */}
            <div className="telemetry-box">
                <h3>Dados de Telemetria DAST</h3>
                <p><strong>URL Alvo:</strong> {scanData?.url || 'N/A'}</p>
                <p><strong>HTML Capturado:</strong> {scanData?.html_size_bytes?.toLocaleString() || 0} bytes</p>
                <p><strong>Logs de Console:</strong> {scanData?.console_log_count || 0} entradas</p>
                <p><strong>Erros de Rede:</strong> {scanData?.network_errors?.length || 0} requisições falhas</p>
            </div>

            {/* Resumo executivo */}
            {resumo && (
                <div className="resumo-box">
                    <h3 style={{ marginBottom: '10px', color: '#818cf8' }}>📋 Resumo Executivo</h3>
                    <div dangerouslySetInnerHTML={{ __html: resumo }} />
                </div>
            )}

            {/* Fingerprint de IA */}
            <div className="fingerprint-box">
                <h3>🤖 Fingerprint de IA — Detecção de Geração Automática</h3>
                {fingerprint ? (
                    <>
                        <div className="fingerprint-header">
                            <span className={`fp-badge ${fingerprint.detectado ? 'fp-detected' : 'fp-undetected'}`}>
                                {fingerprint.detectado ? '🔴 IA Detectada' : '🟢 Não Detectada'}
                            </span>
                            <span className="fp-confidence">Confiança: {fingerprint.confianca || 'N/A'}</span>
                        </div>
                        <div dangerouslySetInnerHTML={{ __html: fingerprint.explicacao }} />
                        {fingerprint.evidencias?.length > 0 && (
                            <ul className="fp-evidencias">
                                {fingerprint.evidencias.map((ev, i) => <li key={i}>{ev}</li>)}
                            </ul>
                        )}
                    </>
                ) : (
                    <p style={{ color: '#52525b' }}>Fingerprint de IA não disponível nesta análise.</p>
                )}
            </div>

            {/* Vulnerabilidades web */}
            <div className="ai-analysis-box">
                <h3>🔴 Vulnerabilidades Detectadas via DOM / DAST</h3>
                {webVulns.length === 0 ? (
                    <p>Nenhuma vulnerabilidade detectada ou falha no parse.</p>
                ) : (
                    webVulns.map((vuln, i) => (
                        <div key={i} className="vuln-entry">
                            <h4 className="vuln-title">
                                {vuln.titulo}
                                <span className={`sev-badge ${severityClass(vuln.severidade)}`}>
                                    {vuln.severidade}
                                </span>
                            </h4>

                            {vuln.categoria && (
                                <p style={{ fontSize: '0.8rem', color: '#52525b', marginBottom: '12px' }}>
                                    Categoria: {vuln.categoria}
                                </p>
                            )}

                            <div className="vuln-section text-block">
                                <h5>Explicação Técnica:</h5>
                                <div dangerouslySetInnerHTML={{ __html: vuln.explicacao }} />
                            </div>

                            {vuln.evidencia_dom && (
                                <div className="vuln-section code-block">
                                    <h5>Evidência no DOM:</h5>
                                    <pre><code>{vuln.evidencia_dom}</code></pre>
                                </div>
                            )}

                            {vuln.mermaid && (
                                <div className="vuln-section diagram-block">
                                    <h5>Mapeamento do Exploit:</h5>
                                    <DiagramRenderer chartCode={vuln.mermaid} />
                                </div>
                            )}

                            {vuln.patch && (
                                <div className="vuln-section code-block">
                                    <h5>Patch / Correção:</h5>
                                    <pre><code>{vuln.patch}</code></pre>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>

            {/* Riscos de Console */}
            <div className="console-risks-box ai-analysis-box">
                <h3>⚠️ Riscos Identificados via Console Logs</h3>
                {risks.length === 0 ? (
                    <p>Nenhum risco de console identificado.</p>
                ) : (
                    risks.map((risk, i) => (
                        <div key={i} className="console-risk-entry">
                            <div className="console-risk-title">{risk.titulo}</div>
                            <div className="console-risk-log">{risk.log_original}</div>
                            <div className="console-risk-desc">{risk.explicacao}</div>
                        </div>
                    ))
                )}
            </div>
        </>
    );
}

// ── Componente Principal ──────────────────────────────────────────────────────
export default function ReportViewer({ scanData, aiAnalysis }) {
    if (aiAnalysis?.error) {
        return (
            <div className="report-viewer">
                <div className="error-log-box">
                    <h3 className="error-title">⚠️ Falha no Núcleo de Inteligência</h3>
                    <div className="error-content">
                        <p><strong>Log de Erro do Back-end:</strong></p>
                        <pre><code>{aiAnalysis.error}</code></pre>
                        <p className="error-hint">
                            Sugestão: Verifique se o modelo selecionado (
                            {aiAnalysis?.status === 'ai_failure' ? 'API Gemini' : 'Processamento'})
                            está disponível ou se há um problema de conectividade com o laboratório.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    const isWebMode = scanData?.mode === 'web';

    return (
        <div className="report-viewer">
            <h2>{isWebMode ? 'Diagnóstico DAST — Web App' : 'Diagnóstico da Base de Dados & Laboratório'}</h2>
            {isWebMode
                ? <WebReport scanData={scanData} aiAnalysis={aiAnalysis} />
                : <InfraReport scanData={scanData} aiAnalysis={aiAnalysis} />
            }
        </div>
    );
}
