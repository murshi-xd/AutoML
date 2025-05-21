import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchRunInfo } from '../useStore/usePipelineController';
import { Spin, Tag, Timeline } from 'antd';
import { ClockCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';

const RunDetail = () => {
    const { runId } = useParams();
    const [info, setInfo] = useState(null);

    useEffect(() => {
        fetchRunInfo(runId).then(setInfo);
    }, [runId]);

    if (!info) {
        return (
            <div className="flex justify-center items-center h-64">
                <Spin tip="Loading Run Details..." size="large" />
            </div>
        );
    }

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed':
                return 'green';
            case 'failed':
                return 'red';
            case 'pending':
                return 'orange';
            default:
                return 'blue';
        }
    };

    return (
        <div className="p-6 space-y-6 bg-gradient-to-tr from-gray-50 to-white shadow-xl rounded-2xl max-w-5xl mx-auto">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-center mb-6 border-b pb-4">
                <div>
                    <h2 className="text-3xl font-bold text-blue-600">Run ID: <span className="text-gray-800">{info.mlflow_run_id}</span></h2>
                    <Tag color={getStatusColor(info.status)} className="mt-2 text-sm px-3 py-1">
                        {info.status.toUpperCase()}
                    </Tag>
                </div>
                <Timeline mode="right" className="mt-4 md:mt-0">
                    <Timeline.Item dot={<ClockCircleOutlined />} color="blue">
                        <strong>Start:</strong> {new Date(info.start_time).toLocaleString()}
                    </Timeline.Item>
                    <Timeline.Item dot={<CheckCircleOutlined />} color="green">
                        <strong>End:</strong> {new Date(info.end_time).toLocaleString()}
                    </Timeline.Item>
                </Timeline>
            </div>

            {/* Metrics */}
            <div className="bg-white rounded-xl shadow p-6">
                <h3 className="text-2xl font-semibold text-blue-500 mb-4">📊 Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {Object.entries(info.metrics || {}).map(([key, val]) => (
                        <div key={key} className="p-4 bg-gray-50 rounded-xl shadow-sm hover:shadow-md transition">
                            <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">{key}</p>
                            <p className="text-xl font-semibold text-gray-900">
                                {typeof val === 'number' ? val.toFixed(4) : val}
                            </p>
                        </div>
                    ))}
                </div>
            </div>



            {/* Parameters */}
            <div className="bg-white rounded-xl shadow p-6">
                <h3 className="text-2xl font-semibold text-blue-500 mb-4">⚙️ Parameters</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {Object.entries(info.params || {}).map(([key, val]) => (
                        <div key={key} className="p-4 bg-gray-50 rounded-xl shadow-sm hover:shadow-md transition">
                            <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">{key}</p>
                            <p className="text-sm font-medium text-gray-800 break-words">
                                {Array.isArray(val) ? val.join(', ') : String(val)}
                            </p>
                        </div>
                    ))}
                </div>
            </div>

        </div>
    );
};

export default RunDetail;
