// src/components/ResponsivePlot.jsx
import React, { useEffect, useRef, forwardRef } from 'react';
import Plot from 'react-plotly.js';
import Plotly from 'plotly.js-dist-min';

const ResponsivePlot = forwardRef(({ data, layout = {}, config = {}, className = '' }, ref) => {
  const plotDivRef = useRef();

  useEffect(() => {
    if (!plotDivRef.current) return;

    const resize = () => Plotly.Plots.resize(plotDivRef.current);
    const observer = new ResizeObserver(resize);
    observer.observe(plotDivRef.current);
    setTimeout(resize, 300); // fallback for delayed layouts

    return () => observer.disconnect();
  }, []);

  // Expose the plot div to parent via ref
  React.useImperativeHandle(ref, () => ({
    getPlotDiv: () => plotDivRef.current?.querySelector('.js-plotly-plot')
  }));

  return (
    <div className={`w-full ${className}`}>
      <div className="aspect-[4/3]" ref={plotDivRef}>
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
});

export default ResponsivePlot;
