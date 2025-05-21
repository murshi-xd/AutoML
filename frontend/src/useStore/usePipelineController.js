// src/useStore/usePipelineController.js
import api from '../lib/axios';
import { toast } from 'react-toastify';

export const fetchExperiments = async (userId) => {
    try {
        const res = await api.get(`list_experiments/${userId}`);
        return res.data;
    } catch (err) {
        toast.error('Failed to load experiments');
        console.error(err);
        return [];
    }
};

export const fetchRuns = async (experimentId) => {
    try {
        const res = await api.get(`list_runs/${experimentId}`);
        return res.data;
    } catch (err) {
        toast.error('Failed to load runs');
        console.error(err);
        return [];
    }
};

export const fetchRunInfo = async (runId) => {
    try {
        const res = await api.get(`experiment_info/${runId}`);
        return res.data;
    } catch (err) {
        toast.error('Failed to load run info');
        console.error(err);
        return null;
    }

};

export const fetchAllRunsByUser = async (userId) => {
    try {
        userId = 'test_666';
        const res = await api.get(`list_all_runs_by_user/${userId}`);
        return res.data;
    } catch (err) {
        toast.error('Failed to load all runs');
        console.error(err);
        return [];
    }
};

export const runPipeline = async (data) => {
    try {
        const res = await api.post('run_pipeline', data);
        return res.data;
    } catch (err) {
        console.error('Pipeline run failed:', err);
        return { status: 'error' };
    }
};

export const fetchRunById = async (runId) => {
  try {
    const res = await api.get(`run_by_id/${runId}`);
    return res.data;
  } catch (err) {
    console.error('Failed to fetch run by ID', err);
    return null;
  }
};
