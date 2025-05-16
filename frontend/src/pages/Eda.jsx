import React, { useEffect, useState } from 'react';
import { fetchDatasets, fetchEdaData } from '../useStore/useDatasetController';
import { Table, Button } from 'antd';
import 'antd/dist/reset.css';
import { Input, Slider } from 'antd';

const EDA = () => {
    const [datasets, setDatasets] = useState([]);
    const [selectedDataset, setSelectedDataset] = useState(null);
    const [edaData, setEdaData] = useState(null);
    const [isDatasetListOpen, setIsDatasetListOpen] = useState(false);
    const [showAllMissing, setShowAllMissing] = useState(false);
    const [showAllSummary, setShowAllSummary] = useState(false);
    const [showAllColumns, setShowAllColumns] = useState(false);
    const [missingValueFilter, setMissingValueFilter] = useState([0, 100]);
    const [columnSearch, setColumnSearch] = useState('');
    const [columnTypeFilter, setColumnTypeFilter] = useState('');
    const [columnNameFilter, setColumnNameFilter] = useState('');


    useEffect(() => {
        const loadDatasets = async () => {
            const data = await fetchDatasets();
            setDatasets(data);
        };
        loadDatasets();
    }, []);

    const handleDatasetSelect = async (datasetId) => {
        try {
            const eda = await fetchEdaData(datasetId);
            setSelectedDataset(datasetId);
            setEdaData(eda);
            setIsDatasetListOpen(false); // Close the dropdown after selection
        } catch (error) {
            console.error(error);
        }
    };

    const getSortedMissingValues = () => {
        const minFilter = missingValueFilter[0];
        const maxFilter = missingValueFilter[1];
        return Object.entries(edaData.eda.missing_values)
            .filter(([column, missing]) => 
                missing > 0 && 
                missing >= minFilter && 
                missing <= maxFilter && 
                column.toLowerCase().includes(columnSearch.toLowerCase())
            )
            .sort((a, b) => b[1] - a[1])
            .map(([column, missing]) => ({ column, missing }));
    };

    const getFilteredSummaryStats = () => {
        const summaryStats = Object.entries(edaData.eda.summary)
            .filter(([column]) => edaData.eda.dtypes[column] !== 'object')
            .map(([column, stats]) => ({ column, ...stats }));
        return summaryStats;
    };


    const getDistinctDataTypes = () => {
    if (!edaData) return [];
    const dataTypes = Object.values(edaData.eda.dtypes);
    return Array.from(new Set(dataTypes)).sort();
};

    const tableRowClass = (record, index) => {
        return index % 2 === 0 ? 'bg-gray-100' : 'bg-gray-200';
    };

    return (
        <div className="space-y-4 px-4 md:px-8">
            {/* Dataset List Dropdown */}
            <div className="bg-gradient-to-r from-gray-100 to-gray-200 p-4 rounded-2xl shadow-md">
                <h2 className="text-xl font-bold mb-4 text-gray-800">Datasets</h2>
                <div className="relative">
                    <button onClick={() => setIsDatasetListOpen(!isDatasetListOpen)} className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white py-2 px-4 rounded-lg mb-2 shadow-lg hover:from-blue-600 hover:to-blue-700">
                        {selectedDataset ? `Selected: ${datasets.find(d => d._id === selectedDataset)?.custom_name || 'Select a Dataset'}` : 'Select a Dataset'}
                    </button>
                    {isDatasetListOpen && (
                        <ul className="absolute bg-white shadow-lg rounded-lg w-full max-h-64 overflow-y-auto z-10">
                            {datasets.map((dataset) => (
                                <li key={dataset._id} onClick={() => handleDatasetSelect(dataset._id)}
                                    className={`p-2 cursor-pointer hover:bg-gray-100 ${selectedDataset === dataset._id ? 'bg-blue-100 font-semibold' : ''}`}>
                                    {dataset.custom_name} - {new Date(dataset.uploaded_at).toLocaleString()}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>

            {/* Dataset Details (Full Width) */}
            {edaData && (
                <div className="bg-gradient-to-r from-white to-gray-50 p-4 rounded-2xl shadow-md">
                    <h2 className="text-xl font-bold mb-4 text-gray-800">Dataset Details - {edaData.custom_name}</h2>
                    <ul className="text-sm space-y-2 mb-4">
                        <li><strong>Rows:</strong> {edaData.eda.shape[0]}</li>
                        <li><strong>Columns:</strong> {edaData.eda.shape[1]}</li>
                        <li><strong>Total Missing Values:</strong> {Object.values(edaData.eda.missing_values).reduce((a, b) => a + b, 0)}</li>
                        <li><strong>File Path:</strong> {edaData.file_path}</li>
                        <li><strong>Uploaded At:</strong> {new Date(edaData.uploaded_at).toLocaleString()}</li>
                        <li><strong>File Name:</strong> {edaData.filename}</li>
                    </ul>
                </div>
            )}

            {/* Dataset Preview */}
            {edaData && (
                <div className="bg-gradient-to-r from-gray-50 to-white p-4 rounded-2xl shadow-md w-full">
                    <h3 className="text-lg font-bold mb-2 text-gray-800">Dataset Preview (First 5 Rows)</h3>
                    <Table dataSource={edaData.eda.head} columns={Object.keys(edaData.eda.head[0] || {}).map(key => ({ title: key, dataIndex: key, key }))} pagination={false} rowClassName={tableRowClass} scroll={{ x: true }} />
                </div>
            )}

            {/* Filtered Missing Values (Exclude Zero, Sorted) */}
            {edaData && getSortedMissingValues().length > 0 && (
                <div className="bg-gradient-to-r from-gray-50 to-white p-4 rounded-2xl shadow-md w-full relative">
                    <h3 className="text-lg font-bold mb-2 text-gray-800">Missing Values</h3>
                    
                    {/* Filter Controls */}
                    <div className="flex flex-col md:flex-row gap-4 mb-4">
                        <Input
                            placeholder="Search by column name"
                            value={columnSearch}
                            onChange={(e) => setColumnSearch(e.target.value)}
                            className="w-full md:w-1/3"
                        />
                        <div className="flex flex-col flex-grow">
                            <label className="text-sm text-gray-700 mb-1">Filter by Missing Values Range</label>
                            <Slider
                                range
                                min={0}
                                max={edaData.eda.shape[0]}
                                defaultValue={[0, edaData.eda.shape[0]]}
                                onChange={(value) => setMissingValueFilter(value)}
                            />
                        </div>
                    </div>
                    
                    {/* Missing Values Table */}
                    <div className={`${showAllMissing ? '' : 'max-h-80 overflow-y-auto'} mb-8`}>
                        <Table dataSource={getSortedMissingValues()} columns={[
                            { title: 'Column', dataIndex: 'column', key: 'column' },
                            { title: 'Missing Values', dataIndex: 'missing', key: 'missing' }
                        ]} pagination={false} rowClassName={tableRowClass} scroll={{ x: true }} />
                    </div>

                    {getSortedMissingValues().length > 8 && (
                        <div className="absolute bottom-4 left-4 right-4">
                            <Button onClick={() => setShowAllMissing(!showAllMissing)} className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600">
                                {showAllMissing ? 'Show Less' : 'Show More'}
                            </Button>
                        </div>
                    )}
                </div>
            )}


            {/* Column Names and Data Types */}
            {edaData && (
                <div className="bg-gradient-to-r from-gray-50 to-white p-4 rounded-2xl shadow-md w-full relative">
                    <h3 className="text-lg font-bold mb-2 text-gray-800">Column Names and Data Types</h3>
                    
                    {/* Filter Controls */}
                    <div className="flex flex-col md:flex-row gap-4 mb-4">
                        <Input
                            placeholder="Search by column name"
                            value={columnNameFilter}
                            onChange={(e) => setColumnNameFilter(e.target.value)}
                            className="w-full md:w-1/3"
                        />
                        <select
                            value={columnTypeFilter}
                            onChange={(e) => setColumnTypeFilter(e.target.value)}
                            className="w-full md:w-1/3 border rounded-lg p-2 bg-white shadow-sm"
                        >
                            <option value="">All Data Types</option>
                            {getDistinctDataTypes().map((dtype) => (
                                <option key={dtype} value={dtype}>{dtype}</option>
                            ))}
                        </select>
                    </div>

                    {/* Column Names and Types Table */}
                    <div className={`${showAllColumns ? '' : 'max-h-80 overflow-y-auto'} mb-8`}>
                        <Table
                            dataSource={Object.entries(edaData.eda.dtypes)
                                .filter(([name, dtype]) => 
                                    name.toLowerCase().includes(columnNameFilter.toLowerCase()) &&
                                    (columnTypeFilter === '' || dtype === columnTypeFilter)
                                )
                                .map(([name, dtype]) => ({ column: name, dtype }))}
                            columns={[
                                { title: 'Column', dataIndex: 'column', key: 'column' },
                                { title: 'Data Type', dataIndex: 'dtype', key: 'dtype' }
                            ]}
                            pagination={false}
                            rowClassName={tableRowClass}
                            scroll={{ x: true }}
                        />
                    </div>

                    {/* Show More / Show Less Button */}
                    {Object.keys(edaData.eda.dtypes).length > 8 && (
                        <div className="absolute bottom-4 left-4 right-4">
                            <Button onClick={() => setShowAllColumns(!showAllColumns)} className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600">
                                {showAllColumns ? 'Show Less' : 'Show More'}
                            </Button>
                        </div>
                    )}
                </div>
            )}



            {/* Summary Statistics */}
            {edaData && getFilteredSummaryStats().length > 0 && (
                <div className="bg-gradient-to-r from-gray-50 to-white p-4 rounded-2xl shadow-md w-full relative">
                    <h3 className="text-lg font-bold mb-2 text-gray-800">Summary Statistics</h3>
                    <div className={`${showAllSummary ? '' : 'max-h-80 overflow-y-auto'} mb-8`}>
                        <Table dataSource={getFilteredSummaryStats()} columns={[
                            { title: 'Column', dataIndex: 'column', key: 'column' },
                            { title: 'Min', dataIndex: 'min', key: 'min' },
                            { title: 'Max', dataIndex: 'max', key: 'max' },
                            { title: 'Mean', dataIndex: 'mean', key: 'mean' },
                            { title: 'Std', dataIndex: 'std', key: 'std' },
                            { title: 'Count', dataIndex: 'count', key: 'count' }
                        ]} pagination={false} rowClassName={tableRowClass} scroll={{ x: true }} />
                    </div>
                    {getFilteredSummaryStats().length > 8 && (
                        <div className="absolute bottom-4 left-4 right-4">
                            <Button onClick={() => setShowAllSummary(!showAllSummary)} className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600">
                                {showAllSummary ? 'Show Less' : 'Show More'}
                            </Button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default EDA;