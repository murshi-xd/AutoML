import api from '../lib/axios'
import { toast } from 'react-toastify';

// Fetch all datasets from the backend
export const fetchDatasets = async () => {
    try {
        const response = await api.get('datasets');
        toast.success('Datasets loaded successfully.');
        return response.data.datasets || [];
    } catch (error) {
        toast.error('Failed to load datasets.');
        console.error(error);
        return [];
    }
};

// Fetch EDA for a specific dataset
// Fetch EDA for a specific dataset
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


// Delete a dataset
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
