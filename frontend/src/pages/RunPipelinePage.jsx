import React, { useEffect, useState } from 'react';
import { fetchDatasets, fetchEdaData } from '../useStore/useDatasetController';
import { runPipeline, fetchAllRunsByUser, fetchRunById } from '../useStore/usePipelineController';
import { useNavigate } from 'react-router-dom';
import { Button, Select, Spin, notification } from 'antd';
import { useAuth } from '../context/AuthContext';


const { Option } = Select;


const RunPipelinePage = () => {
    const [datasets, setDatasets] = useState([]);
    const [columns, setColumns] = useState([]);
    const [selectedDataset, setSelectedDataset] = useState(null);
    const [params, setParams] = useState({});
    const [loading, setLoading] = useState(false);
    const [completedRun, setCompletedRun] = useState(null);
    const [previousRun, setPreviousRun] = useState(null);
    const navigate = useNavigate();
    const { user } = useAuth();

    const strategies = {
        missing: ['mean', 'median', 'most_frequent'],
        scaling: ['standard_scaling', 'minmax_scaling'],
        outlierStrategy: ['zscore', 'iqr'],
        outlierMethod: ['remove', 'cap']
    };

    useEffect(() => {
        fetchDatasets().then(setDatasets);
        fetchAllRunsByUser(user?.id).then(data => {
            if (data.length > 0) {
                const latest = data.sort((a, b) => new Date(b.end_time) - new Date(a.end_time))[0];
                setPreviousRun(latest);
            }
        });
    }, []);

    const handleDatasetChange = async (datasetId) => {
        setSelectedDataset(datasetId);
        const eda = await fetchEdaData(datasetId);
        if (eda) {
            const cols = Object.keys(eda.eda.dtypes || {});
            setColumns(cols);
        }
    };

    const handleParamChange = (key, value) => {
        setParams(prev => ({
            ...prev,
            [key]: value
        }));
    };

    const handleRun = async () => {
        if (!selectedDataset) return;
        const payload = {
            user_id: user.id,
            dataset_id: selectedDataset,
            params
        };
        setLoading(true);
        const result = await runPipeline(payload);
        if (result?.status === 'completed' && result.run_id) {
            // Now fetch full run info using run_id to get mlflow_run_id
            const runInfo = await fetchRunById(result.run_id);
            setLoading(false);
            if (runInfo?.mlflow_run_id) {
                setCompletedRun({ ...runInfo, run_id: result.run_id });
                notification.success({ message: 'Pipeline completed!' });
            } else {
                notification.error({ message: 'Could not retrieve run details.' });
            }
        } else {
            setLoading(false);
            notification.error({ message: 'Pipeline failed or no run ID returned.' });
        }
    };

    const renderDropdown = (label, key, options, isMulti = false, searchable = false) => (
        <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">{label}</label>
            <Select
                mode={isMulti ? 'multiple' : undefined}
                placeholder={label}
                onChange={(v) => handleParamChange(key, v)}
                showSearch={searchable}
                filterOption={(input, option) =>
                    option.children.toLowerCase().includes(input.toLowerCase())
                }
                className="w-full"
            >
                {options.map(opt => (
                    <Option key={opt} value={opt}>{opt}</Option>
                ))}
            </Select>
        </div>
    );

    return (
        <div className="p-6 space-y-6 bg-white rounded-xl shadow-md">
            <h2 className="text-3xl font-bold text-blue-600">⚙️ Run a New Pipeline</h2>

            <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">Select Dataset</label>
                <Select
                    placeholder="Select Dataset"
                    style={{ width: '100%' }}
                    onChange={handleDatasetChange}
                    value={selectedDataset}
                    showSearch
                    filterOption={(input, option) =>
                        option.children.toLowerCase().includes(input.toLowerCase())
                    }
                >
                    {datasets.map(ds => (
                        <Option key={ds._id} value={ds._id}>{ds.custom_name}</Option>
                    ))}
                </Select>
            </div>

            {/* Parameter Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderDropdown("Missing Value Strategy", "missing_value_feature_strategy", strategies.missing)}
                {renderDropdown("Feature Scaling Strategy", "feature_strategy", strategies.scaling)}
                {renderDropdown("Outlier Column", "outlier_column", columns, false, true)}
                {renderDropdown("Outlier Strategy", "outlier_strategy", strategies.outlierStrategy)}
                {renderDropdown("Outlier Method", "outlier_method", strategies.outlierMethod)}
                {renderDropdown("Target Column", "target_column", columns, false, true)}
                {renderDropdown("Feature Columns", "feature_columns", columns, true, true)}
            </div>

            <Button
                type="primary"
                className="bg-blue-600 text-white mt-4"
                onClick={handleRun}
                disabled={loading || !selectedDataset}
            >
                Run Pipeline
            </Button>

            {/* Loader or Result */}
            {loading && (
                <div className="flex justify-center mt-6">
                    <Spin size="large" tip="Running pipeline..." />
                </div>
            )}

            {completedRun?.mlflow_run_id && (
                <div
                    onClick={() => navigate(`/runs/${completedRun.mlflow_run_id}`)}
                    className="mt-6 p-4 rounded-xl shadow hover:shadow-lg bg-green-50 border-l-4 border-green-500 cursor-pointer transition"
                >
                    <h3 className="text-xl font-bold text-green-700">🎉 Run Completed</h3>
                    <p className="text-sm">Run ID: {completedRun.mlflow_run_id}</p>
                    <p className="text-sm text-gray-600">Click to view details</p>
                </div>
            )}

            {!completedRun && previousRun?.mlflow_run_id && (
                <div className="mt-6 p-4 rounded-xl shadow bg-yellow-50 border-l-4 border-yellow-400">
                    <h3 className="text-xl font-bold text-yellow-700">🕒 Last Run</h3>
                    <p className="text-sm">Run ID: {previousRun.mlflow_run_id}</p>
                    <p className="text-sm text-gray-600">Click to view previous run.</p>
                    <Button
                        type="link"
                        onClick={() => navigate(`/runs/${previousRun.mlflow_run_id}`)}
                        className="text-blue-600"
                    >
                        View Last Run
                    </Button>
                </div>
            )}
        </div>
    );
};

export default RunPipelinePage;