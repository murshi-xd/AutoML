// src/useStore/UseEdaController.js
import api from '../lib/axios';

export const fetchDatasets = async (userId) => {
    try {
        const response = await api.get('datasets', {
            params: { user_id: userId }
        });
        return response.data.datasets || [];
    } catch (error) {
        console.error('Failed to load datasets:', error);
        return [];
    }
};

export const fetchEdaData = async (datasetId) => {
    try {
        const response = await api.get(`dataset/${datasetId}/eda`);
        return response.data;
    } catch (error) {
        console.error('Error fetching EDA data:', error);
        return null;
    }
};

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
        console.error('Error generating EDA visual:', error);
        return null;
    }
};

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
        return { success: true, ...response.data };
    } catch (error) {
        console.error('Error saving plot:', error);
        return { success: false };
    }
};

export const getSavedPlots = async (userId) => {
    try {
        const response = await api.get(`get_plots/${userId}`);
        if (Array.isArray(response.data)) return response.data;
        if (Array.isArray(response.data.plots)) return response.data.plots;
        return [];
    } catch (error) {
        console.error('Error fetching saved plots:', error);
        return [];
    }
};

export const deletePlot = async (plotId) => {
    try {
        const response = await api.delete(`delete_plot/${plotId}`);
        return response.data;
    } catch (error) {
        console.error('Error deleting plot:', error);
        return null;
    }
};
