import axios from 'axios';

const BASE = 'http://localhost:8000/api';

export const getAccounts   = ()           => axios.get(`${BASE}/accounts`);
export const getRisk       = (account_id) => axios.get(`${BASE}/risk/${account_id}`);
export const getGraph      = (account_id) => axios.get(`${BASE}/graph/${account_id}`);
export const generateReport= (account_id) => axios.post(`${BASE}/report/${account_id}`);