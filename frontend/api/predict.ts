import axios from 'axios';

const BASE_API = 'http://localhost:8000';

interface PredictResponse {
    prediction: number;    // np. 5
    confidence?: number;   // opcjonalnie: pewność modelu np. 0.98
}

export async function sendImgDigit(img: FormData): Promise<PredictResponse | null> {
    try {
        const response = await axios.post<PredictResponse>(`${BASE_API}/predict`, img);
        return response.data;
    } catch (error) {
        console.error("Błąd przy wysłaniu zdjęcia do backendu", error);
        return null;
    }
}


export async function saveCanvas(data: FormData) {
    try {
        const response = await axios.post(`${BASE_API}/save-img`, data);
        return response.data
    } catch (error) {
        console.error("Błąd przy wysłaniu zdjęcia do backendu", error);
        return null;
    }
}


export async function retrain() {
    try {
        const response = await axios.get(`${BASE_API}/retrain`);
        return response.data
    } catch (error) {
        console.error("Błąd przy retrain - backend", error);
        return null;
    }
}