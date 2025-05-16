import React, { useState, useEffect } from 'react';
import { uploadFile } from '../useStore/useUploadController';
import { fetchDatasets, fetchEdaData,deleteDataset } from '../useStore/useDatasetController';
import { Table } from 'antd';
import 'antd/dist/reset.css';


const Upload = () => {
    const [file, setFile] = useState(null);
    const [customName, setCustomName] = useState("");
    const [datasets, setDatasets] = useState([]);
    const [selectedDataset, setSelectedDataset] = useState(null);

    useEffect(() => {
        const loadDatasets = async () => {
            const data = await fetchDatasets();
            setDatasets(data);
        };
        loadDatasets();
    }, []);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async (event) => {
        event.preventDefault();

        if (!file) return alert("Please select a file to upload.");

        const response = await uploadFile(file, customName, 'user_123');
        if (response && response.file_id) {
            setFile(null);
            setCustomName("");
            const updatedDatasets = await fetchDatasets();
            setDatasets(updatedDatasets);

            // Automatically select the newly uploaded dataset
            const newDataset = updatedDatasets.find(dataset => dataset.file_id === response.file_id);
            if (newDataset) {
                const eda = await fetchEdaData(newDataset._id);
                setSelectedDataset(eda);
            }
        }
    };

    const handleDatasetSelect = async (datasetId) => {
        if (selectedDataset && selectedDataset._id === datasetId) {
            // Deselect the dataset if it's already selected
            setSelectedDataset(null);
        } else {
            const eda = await fetchEdaData(datasetId);
            setSelectedDataset(eda);
        }
    };

    const handleDatasetDelete = async (datasetId) => {
        const confirmed = window.confirm("Are you sure you want to delete this dataset?");
        if (confirmed) {
            const success = await deleteDataset(datasetId);
            if (success) {
                const updatedDatasets = await fetchDatasets();
                setDatasets(updatedDatasets);
                setSelectedDataset(null);
                setEdaData(null);
            }
        }
    };

    // Auto-select the newly uploaded dataset
    useEffect(() => {
        if (datasets.length > 0 && selectedDataset === null) {
            const mostRecentDataset = datasets[datasets.length - 1];
            handleDatasetSelect(mostRecentDataset._id);
        }
    }, [datasets]);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Dataset List */}
            <div className="bg-white p-4 rounded-2xl shadow-md">
                <h2 className="text-xl font-bold mb-4">Existing Datasets</h2>
                <ul className="space-y-2">
                    {datasets.map(dataset => (
                        <li key={dataset._id} className="flex justify-between items-center p-2 rounded-lg cursor-pointer hover:bg-gray-100">
                            <span onClick={() => handleDatasetSelect(dataset._id)} className={selectedDataset && selectedDataset._id === dataset._id ? 'text-blue-600 font-semibold' : ''}>
                                {dataset.custom_name} - {new Date(dataset.uploaded_at).toLocaleString()}
                            </span>
                            <button onClick={() => handleDatasetDelete(dataset._id)} className="text-red-500 hover:text-red-700 ml-2">🗑️</button>
                        </li>
                    ))}
                </ul>
            </div>

            {/* File Upload Form */}
            <div className="bg-white p-4 rounded-2xl shadow-md">
                <h2 className="text-xl font-bold mb-4">Upload File</h2>
                <form onSubmit={handleUpload} className="space-y-4">
                    <input type="file" onChange={handleFileChange} className="w-full border rounded-lg p-2" />
                    <input type="text" value={customName} onChange={(e) => setCustomName(e.target.value)} placeholder="Custom File Name (Optional)" className="w-full border rounded-lg p-2" />
                    <button type="submit" className="bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600">Upload</button>
                </form>
            </div>

            {/* Basic Info (Full Width) */}
            {selectedDataset && (
                <div className="bg-white p-4 rounded-2xl shadow-md w-full col-span-1 md:col-span-2">
                    <h2 className="text-xl font-bold mb-4">Dataset Overview - {selectedDataset.custom_name}</h2>
                    <ul className="text-sm space-y-2">
                        <li><strong>Rows:</strong> {selectedDataset.eda.shape[0]}</li>
                        <li><strong>Columns:</strong> {selectedDataset.eda.shape[1]}</li>
                        <li><strong>Total Missing Values:</strong> {Object.values(selectedDataset.eda.missing_values).reduce((a, b) => a + b, 0)}</li>
                        <li><strong>File Path:</strong> {selectedDataset.file_path}</li>
                    </ul>
                </div>
            )}

            {/* Sample Data Table (Full Width) */}
            {selectedDataset && (
                <div className="bg-white p-4 rounded-2xl shadow-md w-full col-span-1 md:col-span-2">
                    <h3 className="text-xl font-bold mb-4">Sample Data (First 5 Rows)</h3>
                    <Table dataSource={selectedDataset.eda.head} columns={Object.keys(selectedDataset.eda.head[0] || {}).map(key => ({ title: key, dataIndex: key, key }))} pagination={false} scroll={{ x: true }} />
                </div>
            )}
        </div>
    );
};

export default Upload;
