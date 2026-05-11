import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowLeft, Shield, Cpu, Globe, FileText, Zap, Server,
  Eye, Download, GitBranch, Layers, Lock, Search, Brain,
  ChevronDown, ChevronRight, Network, Bug, FileCode
} from 'lucide-react';
import Logo from '../assets/BenTesterLogo.png';
import '../styles/DocumentationPage.css';

const sections = [
  { id: 'visao-geral', label: 'Visão Geral', icon: Eye },
  { id: 'arquitetura', label: 'Arquitetura', icon: Layers },
  { id: 'frontend', label: 'Frontend (React)', icon: Globe },
  { id: 'backend', label: 'Backend (FastAPI)', icon: Server },
  { id: 'modos', label: 'Modos de Análise', icon: Search },
  { id: 'ia', label: 'Motor de IA', icon: Brain },
  { id: 'seguranca', label: 'Segurança', icon: Lock },
  { id: 'stack', label: 'Stack Tecnológica', icon: GitBranch },
];

function CollapsibleSection({ title, icon: Icon, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className={`doc-collapsible ${open ? 'open' : ''}`}>
      <button className="doc-collapsible-header" onClick={() => setOpen(!open)}>
        <div className="doc-collapsible-title">
          {Icon && <Icon size={18} />}
          <span>{title}</span>
        </div>
        {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </button>
      {open && <div className="doc-collapsible-body">{children}</div>}
    </div>
  );
}

export default function DocumentationPage() {
  const [activeSection, setActiveSection] = useState('visao-geral');

  const scrollTo = (id) => {
    setActiveSection(id);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className="doc-container">
      {/* Header */}
      <header className="doc-header">
        <Link to="/" className="doc-back-link">
          <ArrowLeft size={16} /> Voltar ao Painel
        </Link>
        <div className="doc-header-brand">
          <img src={Logo} alt="Ben Tester" className="doc-logo" />
          <div>
            <h1>Documentação</h1>
            <p className="doc-subtitle">Guia completo do funcionamento do Ben Tester</p>
          </div>
        </div>
      </header>

      <div className="doc-layout">
        {/* Sidebar */}
        <nav className="doc-sidebar">
          <ul>
            {sections.map(s => (
              <li key={s.id}>
                <button
                  className={activeSection === s.id ? 'active' : ''}
                  onClick={() => scrollTo(s.id)}
                >
                  <s.icon size={14} />
                  <span>{s.label}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* Content */}
        <main className="doc-content">

          {/* Visão Geral */}
          <section id="visao-geral" className="doc-section">
            <h2><Eye size={22} /> Visão Geral</h2>
            <div className="doc-card">
              <p>
                O <strong>Ben Tester</strong> é uma plataforma de segurança cibernética automatizada
                que utiliza Inteligência Artificial para detectar vulnerabilidades, gerar correções
                (patches) e produzir relatórios executivos em PDF.
              </p>
              <div className="doc-feature-grid">
                <div className="doc-feature-item">
                  <Network size={20} />
                  <h4>Varredura de Rede</h4>
                  <p>Escaneamento Nmap em alvos isolados com detecção de portas e serviços.</p>
                </div>
                <div className="doc-feature-item">
                  <FileText size={20} />
                  <h4>Análise de Arquivos</h4>
                  <p>Upload de arquivos com verificação via API do VirusTotal.</p>
                </div>
                <div className="doc-feature-item">
                  <Brain size={20} />
                  <h4>IA Generativa</h4>
                  <p>Integração com Google Gemini e OpenAI via LangChain.</p>
                </div>
                <div className="doc-feature-item">
                  <Download size={20} />
                  <h4>Relatórios PDF</h4>
                  <p>Geração automática de dossiês executivos via WeasyPrint.</p>
                </div>
              </div>
            </div>
          </section>

          {/* Arquitetura */}
          <section id="arquitetura" className="doc-section">
            <h2><Layers size={22} /> Arquitetura do Sistema</h2>
            <div className="doc-card">
              <div className="doc-arch-diagram">
                <div className="doc-arch-layer">
                  <span className="doc-arch-tag">Frontend</span>
                  <div className="doc-arch-box highlight">
                    <Globe size={16} /> React + Vite
                    <small>Porta 5173</small>
                  </div>
                </div>
                <div className="doc-arch-arrow">↕ HTTP / REST</div>
                <div className="doc-arch-layer">
                  <span className="doc-arch-tag">Backend</span>
                  <div className="doc-arch-box">
                    <Server size={16} /> FastAPI + Uvicorn
                    <small>Porta 8000</small>
                  </div>
                </div>
                <div className="doc-arch-arrow">↕ API Calls</div>
                <div className="doc-arch-layer two-col">
                  <div className="doc-arch-box">
                    <Search size={16} /> Nmap / VirusTotal
                    <small>Scanning</small>
                  </div>
                  <div className="doc-arch-box">
                    <Brain size={16} /> Gemini / OpenAI
                    <small>LangChain</small>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Frontend */}
          <section id="frontend" className="doc-section">
            <h2><Globe size={22} /> Frontend (React)</h2>
            <div className="doc-card">
              <p>Interface construída com <strong>React 19</strong> e bundled com <strong>Vite</strong>.</p>

              <CollapsibleSection title="App.jsx — Componente Raiz" icon={FileCode} defaultOpen>
                <p>Gerencia o estado global da sessão e renderiza os painéis principais:</p>
                <ul>
                  <li><code>sessionData</code> — armazena resultados do scan, análise de IA e caminho do PDF.</li>
                  <li><code>activeProvider</code> — indica se o provedor ativo é Gemini ou OpenAI.</li>
                  <li>Renderiza <code>&lt;ScanPanel&gt;</code>, <code>&lt;ReportViewer&gt;</code> e o painel de download do PDF.</li>
                </ul>
              </CollapsibleSection>

              <CollapsibleSection title="ScanPanel.jsx — Console de Comando" icon={Zap}>
                <p>Formulário principal com dois modos de operação:</p>
                <ul>
                  <li><strong>Modo Link:</strong> Input de IP/Host para varredura de rede via Nmap.</li>
                  <li><strong>Modo Arquivo:</strong> Upload de arquivos para análise via VirusTotal.</li>
                </ul>
                <p>Recursos:</p>
                <ul>
                  <li>Toggle entre provedores Gemini e OpenAI.</li>
                  <li>Seletor dinâmico de modelos (muda conforme o provedor).</li>
                  <li>Feedback visual com spinner de loading e alertas de erro.</li>
                  <li>Chamadas HTTP via Axios para <code>POST /analyze</code> ou <code>POST /analyze-file</code>.</li>
                </ul>
              </CollapsibleSection>

              <CollapsibleSection title="ReportViewer.jsx — Visualização de Resultados" icon={Eye}>
                <p>Exibe os resultados da análise em dois painéis:</p>
                <ul>
                  <li><strong>Telemetria:</strong> Dados do scan (alvo, status, portas abertas com protocolo/produto/versão).</li>
                  <li><strong>Análise de IA:</strong> Vulnerabilidades encontradas com título, explicação técnica, diagrama Mermaid e patch de correção.</li>
                </ul>
              </CollapsibleSection>

              <CollapsibleSection title="DiagramRenderer.jsx — Diagramas Mermaid" icon={GitBranch}>
                <p>Renderiza diagramas de fluxo gerados pela IA usando a biblioteca <strong>Mermaid.js</strong>.</p>
                <ul>
                  <li>Sanitiza caracteres especiais (acentos, parênteses) que quebram o parser.</li>
                  <li>Renderização assíncrona com tratamento de erros.</li>
                  <li>Tema escuro integrado ao design da aplicação.</li>
                </ul>
              </CollapsibleSection>
            </div>
          </section>

          {/* Backend */}
          <section id="backend" className="doc-section">
            <h2><Server size={22} /> Backend (FastAPI)</h2>
            <div className="doc-card">
              <p>API REST construída com <strong>FastAPI</strong> e servida via <strong>Uvicorn</strong>.</p>

              <CollapsibleSection title="Endpoints da API" icon={Zap} defaultOpen>
                <div className="doc-endpoint-list">
                  <div className="doc-endpoint">
                    <span className="doc-method get">GET</span>
                    <code>/</code>
                    <p>Health check — retorna status do servidor.</p>
                  </div>
                  <div className="doc-endpoint">
                    <span className="doc-method post">POST</span>
                    <code>/analyze</code>
                    <p>Modo Infraestrutura: scan Nmap + análise IA textual.</p>
                  </div>
                  <div className="doc-endpoint">
                    <span className="doc-method post">POST</span>
                    <code>/analyze-file</code>
                    <p>Modo Arquivo: upload → VirusTotal → análise IA.</p>
                  </div>
                  <div className="doc-endpoint">
                    <span className="doc-method post">POST</span>
                    <code>/analyze-web</code>
                    <p>Modo DAST: captura Playwright + análise multimodal.</p>
                  </div>
                </div>
              </CollapsibleSection>

              <CollapsibleSection title="scanner.py — Motor de Varredura" icon={Search}>
                <ul>
                  <li>Utiliza <code>python-nmap</code> para escanear portas em alvos isolados.</li>
                  <li>Validação de IP: <strong>bloqueia qualquer IP público</strong> — somente redes privadas.</li>
                  <li>Coleta metadados HTTP (headers, server, x-powered-by) via <code>httpx</code>.</li>
                  <li>Salva resultados em <code>scan_results.json</code>.</li>
                </ul>
              </CollapsibleSection>

              <CollapsibleSection title="ai_engine.py — Motor de IA" icon={Brain}>
                <ul>
                  <li>Suporte dual: <strong>Google Gemini</strong> (via LangChain) e <strong>OpenAI</strong>.</li>
                  <li>Detecção automática do provedor baseado no nome do modelo.</li>
                  <li>Prompt engineering especializado para análise de segurança.</li>
                  <li>Análise multimodal (texto + imagem) para modo DAST.</li>
                  <li>Saída estruturada em JSON com vulnerabilidades, patches e diagramas Mermaid.</li>
                </ul>
              </CollapsibleSection>

              <CollapsibleSection title="report_generator.py — Gerador de PDF" icon={FileText}>
                <ul>
                  <li>Templates HTML via <strong>Jinja2</strong>.</li>
                  <li>Conversão para PDF profissional via <strong>WeasyPrint</strong>.</li>
                  <li>PDFs servidos como arquivos estáticos em <code>/reports/</code>.</li>
                </ul>
              </CollapsibleSection>
            </div>
          </section>

          {/* Modos de Análise */}
          <section id="modos" className="doc-section">
            <h2><Search size={22} /> Modos de Análise</h2>
            <div className="doc-card">
              <div className="doc-modes-grid">
                <div className="doc-mode-card">
                  <div className="doc-mode-icon"><Network size={28} /></div>
                  <h4>Modo Link (Infraestrutura)</h4>
                  <ol>
                    <li>Usuário insere IP/Host do alvo local.</li>
                    <li>Backend executa scan Nmap (<code>-sV -Pn -T4</code>).</li>
                    <li>Resultados enviados para a IA via LangChain.</li>
                    <li>IA retorna vulnerabilidades, patches e diagramas.</li>
                    <li>PDF gerado automaticamente via WeasyPrint.</li>
                  </ol>
                </div>
                <div className="doc-mode-card">
                  <div className="doc-mode-icon"><FileText size={28} /></div>
                  <h4>Modo Arquivo (VirusTotal)</h4>
                  <ol>
                    <li>Usuário faz upload de um arquivo.</li>
                    <li>Backend calcula SHA-256 do arquivo.</li>
                    <li>Consulta hash no VirusTotal (ou envia para análise).</li>
                    <li>Resultados do VirusTotal enviados para a IA.</li>
                    <li>IA interpreta detecções e recomenda ações.</li>
                  </ol>
                </div>
              </div>
            </div>
          </section>

          {/* Motor de IA */}
          <section id="ia" className="doc-section">
            <h2><Brain size={22} /> Motor de IA (LangChain)</h2>
            <div className="doc-card">
              <p>O motor de IA orquestra a comunicação com LLMs usando o framework <strong>LangChain</strong>.</p>
              <div className="doc-table-wrapper">
                <table className="doc-table">
                  <thead>
                    <tr>
                      <th>Provedor</th>
                      <th>Modelos Disponíveis</th>
                      <th>Recursos</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><strong>Google Gemini</strong></td>
                      <td>2.0 Flash, 2.0 Flash Lite, 2.5 Flash, 2.5 Flash Lite, 2.5 Pro</td>
                      <td>Texto + Visão Multimodal</td>
                    </tr>
                    <tr>
                      <td><strong>OpenAI</strong></td>
                      <td>GPT-4o, GPT-4o Mini, GPT-4.1, GPT-4.1 Mini, GPT-4 Turbo, o3-mini, o4-mini</td>
                      <td>Texto + Visão (modelos compatíveis)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div className="doc-info-box">
                <Bug size={16} />
                <p>A saída da IA é sempre um JSON estruturado contendo: <code>titulo</code>, <code>explicacao</code> (HTML), <code>patch</code> (código) e <code>mermaid</code> (diagrama).</p>
              </div>
            </div>
          </section>

          {/* Segurança */}
          <section id="seguranca" className="doc-section">
            <h2><Lock size={22} /> Segurança e Ética</h2>
            <div className="doc-card">
              <div className="doc-warning-banner">
                <Shield size={20} />
                <p><strong>Regra de Ouro:</strong> Todos os testes são executados exclusivamente em ambientes isolados (localhost, Docker, redes privadas). Zero testes em alvos reais.</p>
              </div>
              <ul>
                <li>O scanner <strong>bloqueia automaticamente</strong> qualquer IP público ou externo.</li>
                <li>Apenas IPs privados (RFC 1918), loopback e hostnames do Docker são permitidos.</li>
                <li>O ambiente de testes utiliza <strong>OWASP Juice Shop</strong> via Docker como alvo vulnerável controlado.</li>
                <li>Rede Docker isolada (<code>secops_net</code>) com bridge nativa.</li>
                <li>CORS configurado para aceitar requests do frontend local.</li>
              </ul>
            </div>
          </section>

          {/* Stack */}
          <section id="stack" className="doc-section">
            <h2><GitBranch size={22} /> Stack Tecnológica</h2>
            <div className="doc-card">
              <div className="doc-stack-grid">
                {[
                  { name: 'React 19', desc: 'Interface de usuário', cat: 'Frontend' },
                  { name: 'Vite 5', desc: 'Bundler e dev server', cat: 'Frontend' },
                  { name: 'Lucide React', desc: 'Biblioteca de ícones', cat: 'Frontend' },
                  { name: 'Mermaid.js', desc: 'Diagramas dinâmicos', cat: 'Frontend' },
                  { name: 'Axios', desc: 'Cliente HTTP', cat: 'Frontend' },
                  { name: 'FastAPI', desc: 'Framework da API', cat: 'Backend' },
                  { name: 'Uvicorn', desc: 'Servidor ASGI', cat: 'Backend' },
                  { name: 'python-nmap', desc: 'Varredura de rede', cat: 'Backend' },
                  { name: 'LangChain', desc: 'Orquestração de IA', cat: 'Backend' },
                  { name: 'Jinja2', desc: 'Templates HTML', cat: 'Backend' },
                  { name: 'WeasyPrint', desc: 'Geração de PDF', cat: 'Backend' },
                  { name: 'Docker', desc: 'Containerização', cat: 'Infra' },
                ].map((t, i) => (
                  <div key={i} className="doc-stack-item">
                    <span className={`doc-stack-cat ${t.cat.toLowerCase()}`}>{t.cat}</span>
                    <strong>{t.name}</strong>
                    <small>{t.desc}</small>
                  </div>
                ))}
              </div>
            </div>
          </section>

        </main>
      </div>
    </div>
  );
}
