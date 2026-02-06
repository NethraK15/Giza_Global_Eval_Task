import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
});

export const setAuthToken = (token) => {
  api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
};
