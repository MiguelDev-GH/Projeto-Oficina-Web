import React, { useState } from 'react';
import axios from 'axios';

const MODES = {
    infra: {
        label: 'Infraestrutura',
        icon: '🖧',
        inputLabel: 'Endereço IP do Alvo (Laboratório)',
        placeholder: 'Ex: 172.17.0.1, juice-shop ou localhost:3000',
        buttonText: 'EXECUTAR VARREDURA E ANÁLISE IA',
        buttonLoadingText: 'INICIANDO INFILTRAÇÃO ANALÍTICA...',
        endpoint: (target, model) =>
            `http://localhost:8000/analyze?target=${encodeURIComponent(target)}&model=${encodeURIComponent(model)}`,
        buildPayload: () => ({}),
    },
    web: {
        label: 'Web App',
        icon: '🌐',
        inputLabel: 'URL da Aplicação Web Alvo',
        placeholder: 'https://meu-projeto.com ou http://juice-shop:3000',
        buttonText: 'EXECUTAR DAST MULTIMODAL',
        buttonLoadingText: 'INFILTRANDO APLICAÇÃO WEB...',
        endpoint: () => `http://localhost:8000/analyze-web`,
        buildPayload: (target, model) => ({ target_url: target, model }),
    },
};

export default function ScanPanel({ onScanComplete }) {
    const [activeMode, setActiveMode] = useState('infra');
    const [target, setTarget] = useState('172.17.0.2');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [model, setModel] = useState('gemini-2.5-flash');

    const mode = MODES[activeMode];

    const handleModeSwitch = (newMode) => {
        if (newMode === activeMode) return;
        setActiveMode(newMode);
        setError(null);
        setTarget(newMode === 'infra' ? '172.17.0.2' : 'http://juice-shop:3000');
    };

    const handleScanSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            let response;

            if (activeMode === 'infra') {
                response = await axios.post(mode.endpoint(target, model));
            } else {
                response = await axios.post(mode.endpoint(), mode.buildPayload(target, model));
            }

            if (response.data.status === 'sucesso') {
                onScanComplete(response.data);
            } else {
                const errorMessage =
                    response.data.error || 'Ação bloqueada pelas regras de confinamento seguro.';
                setError(errorMessage);
                onScanComplete({
                    scan_data: response.data.scan_data || null,
                    inteligencia: { error: errorMessage, status: response.data.status },
                    pdf_report: null,
                });
            }
        } catch (err) {
            const errorMessage =
                err.response?.data?.detail || err.message || 'Erro intrusivo na conexão com back-end.';
            setError(errorMessage);
            onScanComplete({
                scan_data: null,
                inteligencia: { error: errorMessage, status: 'connection_failure' },
                pdf_report: null,
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="scan-panel">
            <h2>Console de Comando SecOps</h2>

            {/* ── Sistema de Abas ── */}
            <div className="mode-tabs">
                {Object.entries(MODES).map(([key, m]) => (
                    <button
                        key={key}
                        type="button"
                        className={`tab-btn${activeMode === key ? ' active' : ''}`}
                        onClick={() => handleModeSwitch(key)}
                        disabled={loading}
                    >
                        <span className="tab-icon">{m.icon}</span>
                        {m.label}
                    </button>
                ))}
            </div>

            <p className="warning-text">
                {activeMode === 'infra'
                    ? '⚠️ Somente alvos na sub-rede autorizada local/bridge ou em confinamento seguro devem ser sondados.'
                    : '⚠️ Modo DAST Multimodal: o Playwright capturará HTML, screenshot e logs. Use apenas em alvos autorizados.'}
            </p>

            <form onSubmit={handleScanSubmit}>
                <div className="input-group">
                    <label>{mode.inputLabel}:</label>
                    <input
                        type="text"
                        value={target}
                        onChange={(e) => setTarget(e.target.value)}
                        placeholder={mode.placeholder}
                    />
                </div>

                <div className="input-group">
                    <label>Modelo Gemini:</label>
                    <select
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                        className="model-select"
                    >
                        <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                        <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                        <option value="gemini-2.0-flash">Gemini 2 Flash</option>
                        <option value="gemini-2.0-flash-lite">Gemini 2 Flash Lite</option>
                        <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite</option>
                    </select>
                </div>

                <button type="submit" className="neon-button" disabled={loading}>
                    {loading ? mode.buttonLoadingText : mode.buttonText}
                </button>
            </form>

            {error && (
                <div className="error-alert">
                    <strong>Alerta de Monitoramento!</strong> {error}
                </div>
            )}
        </div>
    );
}
