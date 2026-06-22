// static/js/core/api.js — API client for backend requests
class API {
    // GET request to an API endpoint
    static async get(endpoint) {
        const response = await fetch(`/api/v1${endpoint}`);
        return response.json();
    }
    
    // POST request with JSON body
    static async post(endpoint, data) {
        const response = await fetch(`/api/v1${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }
    
    // PUT request with JSON body
    static async put(endpoint, data) {
        const response = await fetch(`/api/v1${endpoint}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }
    
    // DELETE request to an endpoint
    static async delete(endpoint) {
        const response = await fetch(`/api/v1${endpoint}`, {
            method: 'DELETE'
        });
        return response.json();
    }
}
