import React, { useState } from 'react';
import axios from 'axios';

export default function ScanPanel({ onScanComplete }) {
    const [target, setTarget] = useState('172.17.0.2');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleScanSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        
        try {
            // Chama a orquestração primária do Backend
            const response = await axios.post(`http://localhost:8000/analyze?target=${encodeURIComponent(target)}`);
            
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
                    <label>IP de Alvo Laboratório (Juice Shop / Local):</label>
                    <input 
                        type="text" 
                        value={target} 
                        onChange={(e) => setTarget(e.target.value)} 
                        placeholder="Ex: 172.17.0.2 ou localhost"
                    />
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
