import { ref } from 'vue';
import { useCSRF } from './use_csrf.js';

export function useModels() {
  const { makeSecureRequest } = useCSRF();
  const loading = ref(false);
  const error = ref('');
  const models = ref([]);

  async function fetchModels() {
    loading.value = true;
    error.value = '';
    const apiUrl = import.meta.env.VITE_API_BASE_URL;

    try {
      const response = await makeSecureRequest(`${apiUrl}/models/`, {
        method: 'GET'
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required. Please login again.');
        } else if (response.status === 403) {
          throw new Error('Access denied. You do not have permission to view models.');
        } else {
          throw new Error(`Error fetching models: ${response.status}`);
        }
      }

      const data = await response.json();
      
      if (data.success && data.models) {
        models.value = data.models.map(model => ({
          id: model.id,
          name: model.name,
          version: model.version,
          description: model.description,
          modelType: model.modelType,
          label: `${model.name} (v${model.version})` // Friendly display name
        }));
      } else {
        throw new Error('Invalid response format from server');
      }
      
    } catch (err) {
      error.value = err.message;
      console.error('Models fetch error:', err);
      
      // If authentication error, redirect to login
      if (err.message.includes('Authentication required')) {
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      }
    } finally {
      loading.value = false;
    }
  }

  return { loading, error, models, fetchModels };
}
