// src/pages/EDA.jsx

import React, { useState, useEffect, useRef } from 'react';
import { Button, Select, notification } from 'antd';
import { fetchDatasets, generateEdaVisual } from '../useStore/UseEdaController';
import { fetchEdaData } from '../useStore/useDatasetController';

const { Option } = Select;

const Visuals = () => {
    const [datasets, setDatasets] = useState([]);
    const [selectedDataset, setSelectedDataset] = useState(null);
    const [columns, setColumns] = useState([]);
    const [selectedColumn, setSelectedColumn] = useState('');
    const [selectedColumn2, setSelectedColumn2] = useState('');
    const [plotType, setPlotType] = useState('histogram');
    const [plotUrl, setPlotUrl] = useState(null);
    const [datasetName, setDatasetName] = useState('');

    useEffect(() => {
        const loadDatasets = async () => {
            const data = await fetchDatasets();
            setDatasets(data);
        };
        loadDatasets();
    }, []);

    const handleDatasetSelect = async (datasetId) => {
        setSelectedDataset(datasetId);
        const edaData = await fetchEdaData(datasetId);
        if (edaData) {
            const columnNames = Object.keys(edaData.eda.dtypes || {});
            setColumns(columnNames);
            setDatasetName(edaData.custom_name || "dataset");
            setSelectedColumn('');
            setSelectedColumn2('');
            setPlotUrl(null);
        } else {
            notification.error({ message: 'Failed to load dataset details.' });
        }
    };

    const handleGeneratePlot = async () => {
        if (!selectedDataset || !plotType) {
            notification.error({ message: 'Please select a dataset and plot type.' });
            return;
        }

        const plot = await generateEdaVisual(
            selectedDataset,
            plotType,
            selectedColumn,
            selectedColumn2
        );

        if (plot) {
            setPlotUrl(plot);
            notification.success({ message: 'Plot generated successfully!' });
        } else {
            notification.error({ message: 'Failed to generate plot.' });
        }
    };

    const handleDownload = () => {
        if (plotUrl) {
            const link = document.createElement("a");
            const filename = `${datasetName}_${plotType}.png`;
            link.href = plotUrl;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            notification.success({ message: `Downloaded as ${filename}` });
        }
    };

    return (
        <div className="p-6 space-y-4 bg-white shadow-md rounded-lg">
            <h2 className="text-xl font-semibold">Exploratory Data Analysis (EDA)</h2>

            <Select
                placeholder="Select Dataset"
                style={{ width: 300 }}
                onChange={handleDatasetSelect}
                value={selectedDataset}
            >
                {datasets.map((dataset) => (
                    <Option key={dataset._id} value={dataset._id}>
                        {dataset.custom_name}
                    </Option>
                ))}
            </Select>

            <Select
                placeholder="Select Plot Type"
                style={{ width: 300, marginLeft: 20 }}
                onChange={(value) => setPlotType(value)}
                value={plotType}
            >
                {['histogram', 'boxplot', 'heatmap', 'missing', 'correlation_top_n', 
                  'category_distribution', 'pairplot', 'scatter', 'violin', 'jointplot']
                  .map((type) => (
                    <Option key={type} value={type}>
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                    </Option>
                ))}
            </Select>

            {['scatter', 'jointplot'].includes(plotType) && (
                <>
                    <Select
                        placeholder="Select Column 1"
                        style={{ width: 300 }}
                        onChange={(value) => setSelectedColumn(value)}
                        value={selectedColumn}
                    >
                        {columns.map((col) => (
                            <Option key={col} value={col}>
                                {col}
                            </Option>
                        ))}
                    </Select>

                    <Select
                        placeholder="Select Column 2"
                        style={{ width: 300, marginLeft: 20 }}
                        onChange={(value) => setSelectedColumn2(value)}
                        value={selectedColumn2}
                    >
                        {columns.map((col) => (
                            <Option key={col} value={col}>
                                {col}
                            </Option>
                        ))}
                    </Select>
                </>
            )}

            {['histogram', 'boxplot', 'category_distribution', 'violin'].includes(plotType) && (
                <Select
                    placeholder="Select Column"
                    style={{ width: 300 }}
                    onChange={(value) => setSelectedColumn(value)}
                    value={selectedColumn}
                >
                    {columns.map((col) => (
                        <Option key={col} value={col}>
                            {col}
                        </Option>
                    ))}
                </Select>
            )}

            <Button
                type="primary"
                onClick={handleGeneratePlot}
                className="bg-blue-500 text-white rounded-md px-4 py-2"
            >
                Generate Plot
            </Button>

            {plotUrl && (
                <div className="mt-4">
                    <h3 className="text-lg font-bold">Generated Plot:</h3>
                    <img src={plotUrl} alt="EDA Plot" className="mt-2 rounded-md shadow-lg" />

                    {/* Download Button */}
                    <Button
                        type="primary"
                        onClick={handleDownload}
                        className="bg-green-500 text-white rounded-md px-4 py-2 mt-4"
                    >
                        Download Plot
                    </Button>
                </div>
            )}
        </div>
    );
};

export default Visuals;
