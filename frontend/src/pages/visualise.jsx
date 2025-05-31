import React, { useState, useEffect } from 'react';
import { Button, Select, notification } from 'antd';
import { fetchDatasets, generateEdaVisual } from '../useStore/UseEdaController';
import { fetchEdaData } from '../useStore/useDatasetController';
import { useAuth } from '../context/AuthContext';

const { Option } = Select;

const Visuals = () => {
    const { user } = useAuth();
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
            if (user?._id) {
                const data = await fetchDatasets(user._id);
                setDatasets(data);
            }
        };
        loadDatasets();
    }, [user]);

    const handleDatasetSelect = async (datasetId) => {
        setSelectedDataset(datasetId);
        const edaData = await fetchEdaData(datasetId);
        if (edaData) {
            const columnNames = Object.keys(edaData.eda.dtypes || {});
            setColumns(columnNames);
            setDatasetName(edaData.custom_name || 'dataset');
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
            const link = document.createElement('a');
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
        <div className="px-4 md:px-8 py-6 space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-md space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">Exploratory Data Analysis (EDA)</h2>

                {/* Selectors */}
                <div className="flex flex-wrap gap-4">
                    <Select
                        placeholder="Select Dataset"
                        className="min-w-[250px]"
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
                        className="min-w-[250px]"
                        onChange={(value) => setPlotType(value)}
                        value={plotType}
                    >
                        {[
                            'histogram', 'boxplot', 'heatmap', 'missing', 'correlation_top_n',
                            'category_distribution', 'pairplot', 'scatter', 'violin', 'jointplot'
                        ].map((type) => (
                            <Option key={type} value={type}>
                                {type.charAt(0).toUpperCase() + type.slice(1).replaceAll('_', ' ')}
                            </Option>
                        ))}
                    </Select>
                </div>

                {/* Column Selection */}
                {['scatter', 'jointplot'].includes(plotType) && (
                    <div className="flex flex-wrap gap-4">
                        <Select
                            placeholder="Select Column 1"
                            className="min-w-[250px]"
                            onChange={setSelectedColumn}
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
                            className="min-w-[250px]"
                            onChange={setSelectedColumn2}
                            value={selectedColumn2}
                        >
                            {columns.map((col) => (
                                <Option key={col} value={col}>
                                    {col}
                                </Option>
                            ))}
                        </Select>
                    </div>
                )}

                {['histogram', 'boxplot', 'category_distribution', 'violin'].includes(plotType) && (
                    <div>
                        <Select
                            placeholder="Select Column"
                            className="min-w-[250px]"
                            onChange={setSelectedColumn}
                            value={selectedColumn}
                        >
                            {columns.map((col) => (
                                <Option key={col} value={col}>
                                    {col}
                                </Option>
                            ))}
                        </Select>
                    </div>
                )}

                {/* Generate Button */}
                <div>
                    <Button
                        type="primary"
                        onClick={handleGeneratePlot}
                        className="bg-blue-500 text-white px-5 py-2 rounded-lg hover:bg-blue-600"
                    >
                        Generate Plot
                    </Button>
                </div>

                {/* Plot Output */}
                {plotUrl && (
                    <div className="mt-6 space-y-4">
                        <h3 className="text-lg font-semibold text-gray-800">Generated Plot:</h3>
                        <img
                            src={plotUrl}
                            alt="EDA Plot"
                            className="w-full max-w-4xl rounded-lg shadow-lg"
                        />
                        <Button
                            type="primary"
                            onClick={handleDownload}
                            className="bg-green-500 text-white px-5 py-2 rounded-lg hover:bg-green-600"
                        >
                            Download Plot
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Visuals;
