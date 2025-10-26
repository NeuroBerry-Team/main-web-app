import { ref } from 'vue';
import { useCSRF } from './use_csrf.js';

export function useInference() {
  const { makeSecureRequest } = useCSRF();
  const loading = ref(false);
  const error = ref('');
  const result = ref(null);
  const debug = ref('');

  async function handleInference(selectedFile, modelId = 1) {
    loading.value = true;
    error.value = '';
    result.value = null;
    debug.value = '';
    const apiUrl = import.meta.env.VITE_API_BASE_URL;

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('name', selectedFile.name);
      formData.append('modelId', modelId);

      debug.value += '\nSending image to backend...';

      const inferRes = await makeSecureRequest(`${apiUrl}/inferences/generateInference`, {
        method: 'POST',
        body: formData
      });
      
      debug.value += `\nInference response: status ${inferRes.status}`;
      
      if (!inferRes.ok) {
        if (inferRes.status === 401) {
          throw new Error('Session expired. Please login again.');
        } else if (inferRes.status === 403) {
          throw new Error('Access denied. You do not have permission for this action.');
        } else {
          throw new Error(`Error generating inference: ${inferRes.status}`);
        }
      }
      
      const inferData = await inferRes.json();
      result.value = inferData;
      debug.value += `\nInference completed successfully!`;
      
    } catch (err) {
      error.value = err.message;
      debug.value += `\nError: ${err.message}`;
      console.error('Inference error:', err);
      
      // If authentication error, redirect to login
      if (err.message.includes('Authentication required') || err.message.includes('Session expired')) {
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      }
    } finally {
      loading.value = false;
    }
  }

  return { loading, error, result, debug, handleInference };
}