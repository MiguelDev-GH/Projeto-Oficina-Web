import React, { useState, useRef } from 'react';
import axios from 'axios';

const MODES = { NETWORK: 'network', FILE: 'file' };

export default function ScanPanel({ onScanComplete }) {
    const [mode, setMode] = useState(MODES.NETWORK);
    const [target, setTarget] = useState('172.17.0.2');
    const [file, setFile] = useState(null);
    const [model, setModel] = useState('gemini-2.5-flash');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleScanSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            let response;

            if (mode === MODES.FILE) {
                if (!file) {
                    setError('Selecione um arquivo para análise.');
                    setLoading(false);
                    return;
                }
                const formData = new FormData();
                formData.append('file', file);
                formData.append('model', model);

                response = await axios.post('http://localhost:8000/analyze-file', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
            } else {
                response = await axios.post(
                    `http://localhost:8000/analyze?target=${encodeURIComponent(target)}&model=${encodeURIComponent(model)}`
                );
            }

            if (response.data.status === 'sucesso') {
                onScanComplete(response.data);
            } else {
                setError(response.data.error || 'Ação bloqueada pelas regras de confinamento seguro.');
            }
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Erro intrusivo na conexão com back-end.');
        } finally {
            setLoading(false);
        }
    };

    const handleModeSwitch = (newMode) => {
        setMode(newMode);
        setError(null);
        setFile(null);
    };

    return (
        <div className="scan-panel">
            <form onSubmit={handleScanSubmit} className="scan-form-inner">

                {/* Input central compacto */}
                <div className="central-input-wrapper">
                    {mode === MODES.NETWORK ? (
                        <input
                            id="target-input"
                            type="text"
                            className="central-input"
                            value={target}
                            onChange={(e) => setTarget(e.target.value)}
                            placeholder="IP ou Host — ex: 172.17.0.2, localhost:3000"
                            autoComplete="off"
                        />
                    ) : (
                        <div
                            className={`file-drop-area ${file ? 'has-file' : ''}`}
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <input
                                ref={fileInputRef}
                                type="file"
                                style={{ display: 'none' }}
                                accept=".py,.js,.jsx,.ts,.tsx,.json,.html,.css,.txt"
                                onChange={(e) => setFile(e.target.files[0])}
                            />
                            <span className="file-drop-icon">📄</span>
                            <span className="file-drop-text">
                                {file ? file.name : 'Clique para selecionar um arquivo (.js, .py, .ts…)'}
                            </span>
                            {file && (
                                <span className="file-drop-size">
                                    {(file.size / 1024).toFixed(1)} KB
                                </span>
                            )}
                        </div>
                    )}
                </div>

                {/* Seletor de modelo minimalista */}
                <div className="model-selector-row">
                    <span className="model-label">Modelo:</span>
                    <select
                        id="model-select"
                        className="model-select-minimal"
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                    >
                        <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                        <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                        <option value="gemini-2.0-flash">Gemini 2 Flash</option>
                        <option value="gemini-2.0-flash-lite">Gemini 2 Flash Lite</option>
                        <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite</option>
                        <option value="gemini-3.1-flash-lite">Gemini 3.1 Flash Lite</option>
                        <option value="gemini-3.1-pro">Gemini 3.1 Pro</option>
                    </select>
                </div>

                {/* Botão executar */}
                <button id="execute-btn" type="submit" className="execute-button" disabled={loading}>
                    {loading ? (
                        <span className="btn-loading">
                            <span className="spinner" />
                            INFILTRANDO...
                        </span>
                    ) : (
                        '⚡ EXECUTAR ANÁLISE'
                    )}
                </button>

                {error && (
                    <div className="error-alert">
                        <strong>⚠ Alerta:</strong> {error}
                    </div>
                )}
            </form>

            {/* Botões cápsula na base — seleção de modo */}
            <div className="mode-capsule-bar">
                <button
                    id="mode-network-btn"
                    type="button"
                    className={`mode-capsule ${mode === MODES.NETWORK ? 'active' : ''}`}
                    onClick={() => handleModeSwitch(MODES.NETWORK)}
                >
                    <span className="capsule-icon">🌐</span>
                    Modo Link
                </button>
                <button
                    id="mode-file-btn"
                    type="button"
                    className={`mode-capsule ${mode === MODES.FILE ? 'active' : ''}`}
                    onClick={() => handleModeSwitch(MODES.FILE)}
                >
                    <span className="capsule-icon">📁</span>
                    Modo Arquivo
                </button>
            </div>
        </div>
    );
}
