import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

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
                    const id = `mermaid-svg-${Math.random().toString(36).substr(2, 9)}`;
                    const { svg } = await mermaid.render(id, chartCode);
                    if (isMounted) setSvgContent(svg);
                } catch (error) {
                    // Translated error outputs to English
                    console.error("[ERROR] Failed to render Mermaid:", error);
                    if (isMounted) setSvgContent(`<p style="color:red">Diagram compilation error: ${error.message}</p>`);
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