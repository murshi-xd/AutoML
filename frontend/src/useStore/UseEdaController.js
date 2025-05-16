// src/useStore/useEdaController.js

import api from '../lib/axios';
import { notification } from 'antd';

// Fetch available datasets
export const fetchDatasets = async () => {
    try {
        const response = await api.get('datasets');
        return response.data.datasets || [];
    } catch (error) {
        notification.error({ message: 'Error fetching datasets' });
        console.error('Error fetching datasets:', error);
        return [];
    }
};



// Generate EDA Visualization (Using POST)
export const generateEdaVisual = async (datasetId, plotType, column = "", column2 = "", format = "png", topN = 10) => {
    try {
        const response = await api.post('eda_visual', {
            dataset_id: datasetId,
            plot_type: plotType,
            column,
            column2,
            download_format: format,
            top_n: topN,
        }, {
            responseType: 'blob',
        });
        return URL.createObjectURL(response.data);
    } catch (error) {
        notification.error({ message: 'Error generating EDA visual' });
        console.error('Error generating EDA visual:', error);
        return null;
    }
};
