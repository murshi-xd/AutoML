import React, { useEffect, useState } from 'react';
import { fetchExperiments, fetchAllRunsByUser } from '../useStore/usePipelineController';
import { useNavigate } from 'react-router-dom';

const ExperimentRunsComponent = () => {
    const [activeTab, setActiveTab] = useState('experiments');
    const [experiments, setExperiments] = useState([]);
    const [runs, setRuns] = useState([]);
    const userId = 'test_666';
    const navigate = useNavigate();

    useEffect(() => {
        if (activeTab === 'experiments') {
            fetchExperiments(userId).then(setExperiments);
        } else {
            fetchAllRunsByUser(userId).then(setRuns);
        }
    }, [activeTab]);

const renderCard = (item, type) => (
    <div
        key={type === 'experiment' ? item.mlflow_experiment_id : item.mlflow_run_id}
        className="border p-4 rounded-lg shadow-md hover:bg-gray-50 cursor-pointer w-full"
        onClick={() =>
            type === 'experiment'
                ? navigate(`/experiments/${item.mlflow_experiment_id}`)
                : navigate(`/runs/${item.mlflow_run_id}`)
        }
    >
        <h3 className="text-lg font-bold">
            {type === 'experiment' ? item.dataset_custom_name : `Run ID: ${item.mlflow_run_id}`}
        </h3>
        <p className="text-sm text-gray-600">
            {type === 'experiment'
                ? `Experiment ID: ${item.mlflow_experiment_id}`
                : <>
                    Status: <span className={`font-bold ${item.status === 'completed' ? 'text-green-600' : 'text-red-600'}`}>
                        {item.status}
                    </span>
                </>
            }
        </p>
        {item.end_time && (
            <p className="text-sm text-gray-500">End Time: {new Date(item.end_time).toLocaleString()}</p>
        )}
    </div>
);


    return (
        <div className="p-6 space-y-4 bg-white rounded-xl shadow-md">
            <div className="flex space-x-4 mb-4">
                <button
                    onClick={() => setActiveTab('experiments')}
                    className={`px-4 py-2 rounded-lg ${activeTab === 'experiments' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}
                >
                    Experiments
                </button>
                <button
                    onClick={() => setActiveTab('runs')}
                    className={`px-4 py-2 rounded-lg ${activeTab === 'runs' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}
                >
                    Runs
                </button>
            </div>
            <div className="space-y-4">
                {activeTab === 'experiments'
                    ? experiments.map(exp => renderCard(exp, 'experiment'))
                    : runs.map(run => renderCard(run, 'run'))}
            </div>
        </div>
    );
};

export default ExperimentRunsComponent;
