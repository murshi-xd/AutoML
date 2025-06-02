import React, { useState, useEffect, useRef } from 'react';
import { Button, Select, notification, Tabs, Tooltip } from 'antd';
import { fetchDatasets, fetchEdaData } from '../useStore/useDatasetController';
import { generateEdaVisual, savePlot, getSavedPlots, deletePlot } from '../useStore/UseEdaController';
import { useAuth } from '../context/AuthContext';
import ResponsivePlot from '../components/ResponsivePlot';
import { PulseLoader } from 'react-spinners';

const { Option } = Select;
const { TabPane } = Tabs;

const Visuals = ({ sidebarOpen }) => {
    const { user } = useAuth();
    const [datasets, setDatasets] = useState([]);
    const [selectedDataset, setSelectedDataset] = useState(null);
    const [edaData, setEdaData] = useState(null);
    const [columns, setColumns] = useState([]);
    const [selectedColumn, setSelectedColumn] = useState('');
    const [selectedColumn2, setSelectedColumn2] = useState('');
    const [plotType, setPlotType] = useState('histogram');
    const [plotData, setPlotData] = useState(null);
    const [datasetName, setDatasetName] = useState('');
    const [savedPlots, setSavedPlots] = useState([]);
    const [savedDatasetFilter, setSavedDatasetFilter] = useState('');
    const [loadingPlot, setLoadingPlot] = useState(false);
    const [statusMessage, setStatusMessage] = useState('');
    const plotRefs = useRef({});

    useEffect(() => {
        const loadData = async () => {
            if (user?._id) {
                const data = await fetchDatasets(user._id);
                setDatasets(Array.isArray(data) ? data : []);
                const saved = await getSavedPlots(user._id);
                setSavedPlots(saved);
            }
        };
        loadData();
    }, [user]);

    const handleDatasetSelect = async (datasetId) => {
        setSelectedDataset(datasetId);
        const eda = await fetchEdaData(datasetId);
        if (eda && eda.eda?.dtypes) {
            const cols = Object.keys(eda.eda.dtypes);
            setEdaData(eda);
            setColumns(cols);
            setDatasetName(eda.custom_name || 'dataset');
            setSelectedColumn('');
            setSelectedColumn2('');
            setPlotData(null);
            setStatusMessage('');
        } else {
            notification.error({ message: 'Dataset not found or failed to fetch EDA.' });
        }
    };

    const handleGeneratePlot = async () => {
        if (!selectedDataset || !plotType) {
            notification.error({ message: 'Select dataset and plot type.' });
            return;
        }

        setLoadingPlot(true);
        const response = await generateEdaVisual(selectedDataset, plotType, selectedColumn, selectedColumn2);
        setLoadingPlot(false);

        if (response && response.data && response.layout) {
            setPlotData(response);
            setStatusMessage('');
            notification.success({ message: 'Plot generated!' });
        } else if (response && response.error) {
            setPlotData(null);
            setStatusMessage(response.error);
            notification.info({ message: response.error });
        } else {
            setPlotData(null);
            setStatusMessage('Failed to generate plot.');
            notification.error({ message: 'Failed to generate plot.' });
        }
    };

    const handleSavePlot = async () => {
        if (!plotData || !user?._id) return;
        const result = await savePlot({
            user_id: user._id,
            dataset_id: selectedDataset,
            plot_type: plotType,
            column: selectedColumn || selectedColumn2,
            plot_data: plotData
        });
        if (result.success) {
            notification.success({ message: 'Plot saved!' });
            const saved = await getSavedPlots(user._id);
            setSavedPlots(saved);
        } else {
            notification.error({ message: 'Failed to save plot.' });
        }
    };

    const handleDeletePlot = async (plotId) => {
        if (!window.confirm('Delete this plot?')) return;
        const result = await deletePlot(plotId);
        if (result?.message) {
            const saved = await getSavedPlots(user._id);
            setSavedPlots(saved);
            notification.success({ message: 'Plot deleted.' });
        } else {
            notification.error({ message: 'Failed to delete plot.' });
        }
    };

    const handleDownloadPlot = (plot, index) => {
        const a = document.createElement('a');
        a.download = `${plot.title || 'plot'}_${index + 1}.json`;
        a.href = URL.createObjectURL(new Blob([JSON.stringify(plot.plot_json)], { type: 'application/json' }));
        a.click();
    };

    // New: Download as image handler
    const handleDownloadPlotImage = async (plot, idx) => {
        const ref = plotRefs.current[plot._id];
        if (ref && ref.getPlotDiv) {
            const plotDiv = ref.getPlotDiv();
            if (plotDiv && window.Plotly) {
                const dataUrl = await window.Plotly.toImage(plotDiv, { format: 'png', height: 600, width: 800 });
                const a = document.createElement('a');
                a.href = dataUrl;
                a.download = `${plot.title || 'plot'}_${idx + 1}.png`;
                a.style.display = 'none';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }
        }
    };

    const filteredSavedPlots = savedDatasetFilter
        ? savedPlots.filter(p => p.dataset_id === savedDatasetFilter)
        : savedPlots;

    return (
        <div className="pt-24 p-6 space-y-6 bg-white shadow-md rounded-xl mx-4 md:mx-8">
            <h2 className="text-2xl font-semibold text-gray-800">🧠 Smart EDA Workspace</h2>
            <Tabs defaultActiveKey="1">
                <TabPane tab="🔍 Generate Plot" key="1">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Select
                            placeholder="Select Dataset"
                            value={selectedDataset}
                            onChange={handleDatasetSelect}
                            className="w-full"
                            showSearch
                            optionFilterProp="children"
                        >
                            {datasets.map((d) => (
                                <Option key={d._id} value={d._id}>{d.custom_name}</Option>
                            ))}
                        </Select>
                        <Select
                            placeholder="Select Plot Type"
                            value={plotType}
                            onChange={(v) => setPlotType(v)}
                            className="w-full"
                        >
                            {[ 'histogram', 'boxplot', 'heatmap', 'missing', 'correlation_top_n', 'category_distribution', 'pairplot', 'scatter', 'violin', 'jointplot' ].map((t) => (
                                <Option key={t} value={t}>{t.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</Option>
                            ))}
                        </Select>
                    </div>
                    {(plotType !== 'heatmap' && plotType !== 'pairplot' && plotType !== 'missing') && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                            {['scatter', 'jointplot'].includes(plotType) ? (
                                <>
                                    <Select
                                        showSearch
                                        placeholder="Column 1"
                                        value={selectedColumn}
                                        onChange={setSelectedColumn}
                                        className="w-full"
                                        filterOption={(input, option) => option?.value?.toLowerCase().includes(input.toLowerCase())}
                                    >
                                        {columns.map((col) => (<Option key={col} value={col}>{col}</Option>))}
                                    </Select>
                                    <Select
                                        showSearch
                                        placeholder="Column 2"
                                        value={selectedColumn2}
                                        onChange={setSelectedColumn2}
                                        className="w-full"
                                        filterOption={(input, option) => option?.value?.toLowerCase().includes(input.toLowerCase())}
                                    >
                                        {columns.map((col) => (<Option key={col} value={col}>{col}</Option>))}
                                    </Select>
                                </>
                            ) : (
                                <Select
                                    showSearch
                                    placeholder="Column"
                                    value={selectedColumn}
                                    onChange={setSelectedColumn}
                                    className="w-full md:col-span-2"
                                    filterOption={(input, option) => option?.value?.toLowerCase().includes(input.toLowerCase())}
                                >
                                    {columns.map((col) => (<Option key={col} value={col}>{col}</Option>))}
                                </Select>
                            )}
                        </div>
                    )}
                    <div className="flex flex-wrap gap-4 mt-4">
                        <Button onClick={handleGeneratePlot} className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">Generate Plot</Button>
                        <Button onClick={handleSavePlot} className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700">Save Plot</Button>
                    </div>
                    {statusMessage && (
                        <div className="text-center text-gray-600 font-medium mt-4">
                            {statusMessage}
                        </div>
                    )}
                    {loadingPlot ? (
                        <div className="flex justify-center items-center py-10">
                            <PulseLoader color="#3B82F6" />
                        </div>
                    ) : (
                        plotData && plotData.data && plotData.layout && (
                            <div className="mt-6 text-center w-full">
                                <h3 className="text-lg font-semibold mb-4">📊 Generated Plot</h3>
                                <div className="w-full h-full bg-white p-4 rounded shadow">
                                    <ResponsivePlot data={plotData.data} layout={plotData.layout} />
                                </div>
                            </div>
                        )
                    )}
                </TabPane>
                <TabPane tab="📁 Saved Plots" key="2">
                    <div className="mb-4">
                        <Select
                            placeholder="Filter by Dataset"
                            value={savedDatasetFilter || undefined}
                            onChange={setSavedDatasetFilter}
                            allowClear
                            className="w-full md:w-1/3"
                        >
                            {datasets.map(d => (
                                <Option key={d._id} value={d._id}>{d.custom_name}</Option>
                            ))}
                        </Select>
                    </div>
                    {filteredSavedPlots.length === 0 ? (
                        <p className="text-gray-500">No plots saved{savedDatasetFilter ? ' for selected dataset' : ''}.</p>
                    ) : (
                        <div className="space-y-8">
                            {[...new Set(filteredSavedPlots.map(p => p.dataset_id))].map(datasetId => {
                                const datasetName = datasets.find(d => d._id === datasetId)?.custom_name || 'Unknown Dataset';
                                const plots = filteredSavedPlots.filter(p => p.dataset_id === datasetId);
                                return (
                                    <div key={datasetId}>
                                        <h3 className="text-lg font-bold text-gray-800 mb-2">📂 {datasetName}</h3>
                                        <div className="space-y-6">
                                            {plots.map((plot, idx) => (
                                                <div key={plot._id} className="bg-gray-100 p-4 rounded shadow w-full">
                                                    <h4 className="font-semibold mb-2">{plot.title}</h4>
                                                    <div className="w-full h-full bg-white p-4 rounded">
                                                        <ResponsivePlot
                                                            ref={el => plotRefs.current[plot._id] = el}
                                                            data={plot.plot_json?.data}
                                                            layout={plot.plot_json?.layout}
                                                        />
                                                    </div>
                                                    <div className="flex justify-end mt-2 gap-2">
                                                        <Tooltip title="Download Image">
                                                            <Button onClick={() => handleDownloadPlotImage(plot, idx)}>
                                                                Download Image
                                                            </Button>
                                                        </Tooltip>
                                                        <Tooltip title="Delete Plot">
                                                            <Button danger onClick={() => handleDeletePlot(plot._id)}>
                                                                Delete
                                                            </Button>
                                                        </Tooltip>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </TabPane>
            </Tabs>
        </div>
    );
};

export default Visuals;
