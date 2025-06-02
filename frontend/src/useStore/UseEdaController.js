// src/useStore/UseEdaController.js

import api from '../lib/axios';
import { toast } from 'react-toastify';

// ✅ Fetch available datasets
export const fetchDatasets = async (userId) => {
    try {
        const response = await api.get('datasets', {
            params: { user_id: userId }
        });
        return response.data.datasets || [];
    } catch (error) {
        console.error('Failed to load datasets:', error);
        toast.error('Failed to load datasets.');
        return [];
    }
};

// ✅ Fetch EDA summary for a dataset
export const fetchEdaData = async (datasetId) => {
    try {
        const response = await api.get(`dataset/${datasetId}/eda`);
        return response.data;
    } catch (error) {
        console.error('Error fetching EDA data:', error);
        toast.error('Failed to fetch EDA data.');
        return null;
    }
};

// ✅ Generate EDA visualization plot
export const generateEdaVisual = async (datasetId, plotType, column = "", column2 = "", top_n = 10) => {
    try {
        const response = await api.post(`eda_visual`, {
            dataset_id: datasetId,
            plot_type: plotType,
            column,
            column2,
            top_n,
            format: 'json'
        });
        return response.data;
    } catch (error) {
        if (error.response?.data?.error) {
            toast.info(error.response.data.error); // expected user message (e.g. no missing values)
            return error.response.data;
        }
        console.error('Error generating EDA visual:', error);
        toast.error('Failed to generate plot.');
        return null;
    }
};

// ✅ Save a generated plot
export const savePlot = async ({ user_id, dataset_id, plot_type, column, plot_data }) => {
    try {
        const response = await api.post(`save_plot`, {
            user_id,
            dataset_id,
            plot_type,
            columns: [column],
            plot_json: plot_data,
            title: `${plot_type} - ${column}`
        });
        toast.success('Plot saved successfully!');
        return { success: true, ...response.data };
    } catch (error) {
        console.error('Error saving plot:', error);
        toast.error('Failed to save plot.');
        return { success: false };
    }
};

// ✅ Fetch all saved plots for a user
export const getSavedPlots = async (userId) => {
    try {
        const response = await api.get(`get_plots/${userId}`);
        if (Array.isArray(response.data)) return response.data;
        if (Array.isArray(response.data.plots)) return response.data.plots;
        return [];
    } catch (error) {
        console.error('Error fetching saved plots:', error);
        toast.error('Failed to load saved plots.');
        return [];
    }
};

// ✅ Delete a saved plot
export const deletePlot = async (plotId) => {
    try {
        const response = await api.delete(`delete_plot/${plotId}`);
        toast.success('Plot deleted.');
        return response.data;
    } catch (error) {
        console.error('Error deleting plot:', error);
        toast.error('Failed to delete plot.');
        return null;
    }
};
