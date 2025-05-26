import api from '../lib/axios';
import { toast } from 'react-toastify';

// ✅ Fetch datasets filtered by user_id
export const fetchDatasets = async (userId) => {
    try {
        const response = await api.get('datasets', {
            params: { user_id: userId }
        });
        toast.success('Datasets loaded successfully.');
        return response.data.datasets || [];
    } catch (error) {
        toast.error('Failed to load datasets.');
        console.error(error);
        return [];
    }
};

// ✅ Fetch EDA for a specific dataset
export const fetchEdaData = async (datasetId) => {
    try {
        const response = await api.get(`datasets/${datasetId}`);
        toast.success('EDA data loaded successfully.');
        return response.data.dataset || {};
    } catch (error) {
        toast.error('Failed to load EDA data.');
        console.error(error);
        return null;
    }
};

// ✅ Delete a dataset
export const deleteDataset = async (datasetId) => {
    try {
        await api.delete(`datasets/${datasetId}`);
        toast.success('Dataset deleted successfully.');
        return true;
    } catch (error) {
        toast.error('Failed to delete dataset.');
        console.error(error);
        return false;
    }
};
