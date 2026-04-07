import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

// Configura o visual do diagrama (Dark mode para combinar com estética SecOps)
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
});

export default function DiagramRenderer({ chartCode }) {
    const ref = useRef(null);
    const [svgContent, setSvgContent] = useState('');

    useEffect(() => {
        let isMounted = true;
        
        async function renderDiagram() {
            if (chartCode) {
                try {
                    // ID aleatório para evitar colisão no DOM caso existam vários gráficos
                    const id = `mermaid-svg-${Math.random().toString(36).substr(2, 9)}`;
                    const { svg } = await mermaid.render(id, chartCode);
                    if (isMounted) setSvgContent(svg);
                } catch (error) {
                    console.error("Falha ao reinderizar Mermaid:", error);
                    if (isMounted) setSvgContent(`<p style="color:red">Erro ao compilar diagrama: ${error.message}</p>`);
                }
            }
        }

        renderDiagram();
        return () => { isMounted = false; };
    }, [chartCode]);

    return (
        <div 
            className="diagram-container" 
            ref={ref} 
            dangerouslySetInnerHTML={{ __html: svgContent }} 
            style={{ padding: '20px', background: '#1e1e1e', borderRadius: '8px', overflowX: 'auto', border: '1px solid #333' }}
        />
    );
}
