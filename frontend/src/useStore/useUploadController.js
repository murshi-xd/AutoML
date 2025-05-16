import api from '../lib/axios';
import { toast } from 'react-toastify';

// Upload a file to the backend
export const uploadFile = async (file, customName, userId = 'default_user') => {
    try {
        if (!file) throw new Error('No file selected');
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('custom_name', customName || file.name.split('.')[0]);
        formData.append('user_id', userId);

        console.log("FormData:", Object.fromEntries(formData.entries()));

        const response = await api.post('upload_file', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        
        toast.success('File uploaded successfully!');
        console.log(response.data);
        return response.data;
    } catch (error) {
        if (error.response && error.response.data) {
            toast.error(error.response.data.error || 'File upload failed. Please try again.');
        } else {
            toast.error(error.message);
        }
        console.error(error);
        return null;
    }
};
