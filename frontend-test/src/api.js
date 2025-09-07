import axios from 'axios';

const BASE_URL = 'http://localhost:5000';

export const sendMessage = (message) =>
  axios.post(`${BASE_URL}/chat`, { message }, { withCredentials: true });

export const uploadPDF = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return axios.post(`${BASE_URL}/upload_pdf`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    withCredentials: true,
  });
};

export const login = (username, password) =>
  axios.post(`${BASE_URL}/login`, { username, password }, { withCredentials: true });
