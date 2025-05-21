import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchRuns } from '../useStore/usePipelineController';

const RunList = () => {
    const { experimentId } = useParams();
    const [runs, setRuns] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        if (experimentId) {
            fetchRuns(experimentId).then(setRuns);
        }
    }, [experimentId]);

    return (
        <div className="p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-4">Runs for Experiment ID: {experimentId}</h2>
            <div className="space-y-4">
                {runs.map((run) => (
                    <div
                        key={run.mlflow_run_id}
                        className="border p-4 rounded-lg shadow hover:bg-gray-50 cursor-pointer"
                        onClick={() => navigate(`/runs/${run.mlflow_run_id}`)}
                    >
                        <h3 className="font-semibold text-lg">Run ID: {run.mlflow_run_id}</h3>
                        <p>Status: <span className={`font-bold ${run.status === 'completed' ? 'text-green-600' : 'text-red-600'}`}>{run.status}</span></p>
                        {run.end_time && <p className="text-sm text-gray-500">End Time: {new Date(run.end_time).toLocaleString()}</p>}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RunList;
