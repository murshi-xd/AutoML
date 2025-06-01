// src/components/ResponsivePlot.jsx
import React, { useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';
import Plotly from 'plotly.js-dist-min';

const ResponsivePlot = ({ data, layout = {}, config = {}, className = '' }) => {
  const plotRef = useRef();

  useEffect(() => {
    if (!plotRef.current) return;

    const resize = () => Plotly.Plots.resize(plotRef.current);
    const observer = new ResizeObserver(resize);
    observer.observe(plotRef.current);
    setTimeout(resize, 300); // fallback for delayed layouts

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={plotRef} className={`w-full ${className}`}>
      <div className="aspect-[4/3]">
        <Plot
          data={data}
          layout={{
            autosize: true,
            margin: { t: 40, l: 40, r: 20, b: 40 },
            ...layout
          }}
          config={{ responsive: true, ...config }}
          useResizeHandler
          style={{ width: '100%', height: '100%' }}
          className="w-full h-full"
        />
      </div>
    </div>
  );
};

export default ResponsivePlot;
