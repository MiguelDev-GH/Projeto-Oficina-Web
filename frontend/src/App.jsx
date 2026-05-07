import React, { useState } from 'react';
import { ShieldCheck, Download, Cpu } from 'lucide-react';
import ScanPanel from './components/ScanPanel';
import ReportViewer from './components/ReportViewer';
import Logo from './assets/BenTesterLogo.png';
import './App.css';

function App() {
  const [sessionData, setSessionData] = useState({
    scanData: null,
    aiAnalysis: null,
    pdfPath: null
  });

  const handleScanComplete = (data) => {
    setSessionData({
      scanData: data.scan_data,
      aiAnalysis: data.inteligencia,
      pdfPath: data.pdf_report
    });
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-brand">
          <img src={Logo} alt="Ben Tester Logo" />
          <h1>Ben Tester</h1>
        </div>
        <div className="status-indicator">
          <ShieldCheck size={14} color="#34d399" />
          LangChain &amp; Gemini Ativo
        </div>
      </header>

      <main className="main-content">
        <ScanPanel onScanComplete={handleScanComplete} />

        {sessionData.scanData && (
          <ReportViewer
            scanData={sessionData.scanData}
            aiAnalysis={sessionData.aiAnalysis}
          />
        )}

        {sessionData.pdfPath && (
          <div className="pdf-download-panel slide-up" style={{ animationDelay: '0.2s' }}>
            <h3>Relatório Operacional Compilado</h3>
            <p>Dossiê em padrão executivo forjado via WeasyPrint.</p>
            <a
              href={`http://localhost:8000${sessionData.pdfPath}`}
              target="_blank"
              rel="noopener noreferrer"
              className="download-button"
            >
              <Download size={16} style={{ marginRight: '8px' }} /> ACESSAR PDF SEGREGADO
            </a>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
