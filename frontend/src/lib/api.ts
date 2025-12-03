/**
 * API Client for Salem Portfolio Analysis Backend
 * Centralized API communication layer
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  SimulationRequest,
  SimulationResponse,
  ModelInputs,
  AssumptionPreset,
  ValidationResult,
  HealthCheck,
} from '../types';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60 second timeout for simulations
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[API] Response from ${response.config.url}:`, response.status);
        return response;
      },
      (error: AxiosError) => {
        console.error('[API] Error:', error.response?.status, error.message);
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async healthCheck(): Promise<HealthCheck> {
    const response = await this.client.get<HealthCheck>('/health');
    return response.data;
  }

  // Run Monte Carlo simulation
  async runSimulation(request: SimulationRequest): Promise<SimulationResponse> {
    const response = await this.client.post<SimulationResponse>(
      '/simulation/run',
      request
    );
    return response.data;
  }

  // Validate inputs
  async validateInputs(inputs: ModelInputs): Promise<ValidationResult> {
    const response = await this.client.post<ValidationResult>(
      '/simulation/validate',
      inputs
    );
    return response.data;
  }

  // Run sensitivity analysis
  async runSensitivityAnalysis(
    inputs: ModelInputs,
    parameter: string,
    variations: number[]
  ): Promise<any> {
    const response = await this.client.post('/simulation/sensitivity', {
      inputs,
      parameter,
      variations,
    });
    return response.data;
  }

  // Get all assumption presets
  async getPresets(): Promise<AssumptionPreset[]> {
    const response = await this.client.get<AssumptionPreset[]>('/presets');
    return response.data;
  }

  // Get specific preset
  async getPreset(name: string): Promise<AssumptionPreset> {
    const response = await this.client.get<AssumptionPreset>(`/presets/${name}`);
    return response.data;
  }

  // Expose the axios client for direct access
  get axiosClient(): AxiosInstance {
    return this.client;
  }
}

// Singleton instance
const apiClient = new ApiClient();

export default apiClient;
