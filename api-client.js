// API Client untuk mengambil data realtime dari backend
class LuxGrowAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    // Ambil data lux
    async getLuxData() {
        try {
            const response = await fetch(`${this.baseURL}/api/realtime/lux`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching lux data:', error);
            return null;
        }
    }

    // Ambil data temperature & humidity
    async getDHTData() {
        try {
            const response = await fetch(`${this.baseURL}/api/realtime/dht`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching DHT data:', error);
            return null;
        }
    }

    // Ambil kondisi cahaya
    async getCondition() {
        try {
            const response = await fetch(`${this.baseURL}/api/realtime/condition`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching condition data:', error);
            return null;
        }
    }

    // Ambil semua data sekaligus
    async getAllData() {
        const [lux, dht, condition] = await Promise.all([
            this.getLuxData(),
            this.getDHTData(),
            this.getCondition()
        ]);

        return {
            lux: lux,
            temperature: dht?.temperature,
            humidity: dht?.humidity,
            condition: condition?.klasifikasi,
            timestamp: lux?.timestamp || new Date().toISOString()
        };
    }

    // Auto-update dengan callback
    startAutoUpdate(callback, interval = 5000) {
        const updateData = async () => {
            const data = await this.getAllData();
            if (callback && typeof callback === 'function') {
                callback(data);
            }
        };

        // Update pertama kali
        updateData();

        // Set interval untuk update berkala
        return setInterval(updateData, interval);
    }

    // Stop auto-update
    stopAutoUpdate(intervalId) {
        if (intervalId) {
            clearInterval(intervalId);
        }
    }
}

// Inisialisasi API client
const luxGrowAPI = new LuxGrowAPI();

// Contoh penggunaan:
// 1. Ambil data sekali
// luxGrowAPI.getAllData().then(data => console.log(data));

// 2. Auto-update dengan callback
// const intervalId = luxGrowAPI.startAutoUpdate((data) => {
//     console.log('Updated data:', data);
//     // Update UI di sini
// });

// 3. Stop auto-update
// luxGrowAPI.stopAutoUpdate(intervalId);