import React, { useState } from 'react';
import axios from 'axios';

export default function ScanPanel({ onScanComplete }) {
    const [target, setTarget] = useState('172.17.0.2');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [model, setModel] = useState('gemini-2.5-flash');
    const handleScanSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        
        try {
            // Chama a orquestração primária do Backend, enviando modelo selecionado
            const response = await axios.post(`http://localhost:8000/analyze?target=${encodeURIComponent(target)}&model=${encodeURIComponent(model)}`);
            
            if (response.data.status === "sucesso") {
                onScanComplete(response.data);
            } else {
                setError(response.data.error || "Ação bloqueada pelas regras de confinamento seguro.");
            }
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Erro intrusivo na conexão com back-end.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="scan-panel">
            <h2>Console de Comando SecOps</h2>
            <p className="warning-text">Aviso: Somente alvos na sub-rede autorizada local/bridge ou em confinamento seguro devem ser sondados.</p>
            
            <form onSubmit={handleScanSubmit}>
                <div className="input-group">
                    <label>IP de Alvo Laboratório (Juice Shop / Local / Host):</label>
                    <input 
                        type="text" 
                        value={target} 
                        onChange={(e) => setTarget(e.target.value)} 
                        placeholder="Ex: 172.17.0.2, juice-shop ou localhost:3000"
                    />
                </div>
                    <div className="input-group">
                        <label>Modelo Gemini:</label>
                        <select value={model} onChange={(e) => setModel(e.target.value)} className="model-select">
                            <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                            <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                            <option value="gemini-2.0-flash">Gemini 2 Flash</option>
                            <option value="gemini-2.0-flash-lite">Gemini 2 Flash Lite</option>
                            <option value="gemini-3.0-flash">Gemini 3 Flash</option>
                            <option value="gemini-3.1-flash-lite">Gemini 3.1 Flash Lite</option>
                            <option value="gemini-3.1-pro">Gemini 3.1 Pro</option>
                            <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite</option>
                        </select>
                    </div>
                
                <button type="submit" className="neon-button" disabled={loading}>
                    {loading ? "INICIANDO INFILTRAÇÃO ANALÍTICA..." : "EXECUTAR VARREDURA E ANÁLISE IA"}
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
