import { ref } from 'vue';
import { useCSRF } from './use_csrf.js';

export function useInference() {
  const { makeSecureRequest } = useCSRF();
  const loading = ref(false);
  const error = ref('');
  const result = ref(null);
  const debug = ref('');

  async function handleInference(selectedFile) {
    loading.value = true;
    error.value = '';
    result.value = null;
    debug.value = '';
    const apiUrl = import.meta.env.VITE_API_BASE_URL;

    try {
      debug.value += '\nSoliciting presigned URL...';
      const presignedRes = await makeSecureRequest(`${apiUrl}/inferences/getBaseImgPresignedUrls`, {
        method: 'GET'
      });
      
      debug.value += `\nPresigned response: status ${presignedRes.status}`;
      
      if (!presignedRes.ok) {
        if (presignedRes.status === 401) {
          throw new Error('Authentication required. Please login again.');
        } else if (presignedRes.status === 403) {
          throw new Error('Access denied. You do not have permission for this action.');
        } else {
          throw new Error(`Error getting upload URL: ${presignedRes.status}`);
        }
      }

      const presignedText = await presignedRes.text();
      debug.value += `\nPresigned response (raw): ${presignedText}`;
      
      let uploadURL, liveURL, imgObjectKey;
      try {
        ({ uploadURL, liveURL, imgObjectKey } = JSON.parse(presignedText));
      } catch (e) {
        throw new Error('Invalid response from server');
      }

      debug.value += '\nUploading image to MinIO...';
      const uploadRes = await fetch(uploadURL, {
        method: 'PUT',
        body: selectedFile,
        headers: { 'Content-Type': selectedFile.type }
      });
      
      debug.value += `\nUpload response: status ${uploadRes.status}`;
      if (!uploadRes.ok) {
        throw new Error('Error uploading image to storage');
      }

      const payload = {
        name: selectedFile.name,
        imgUrl: liveURL,
        imgObjectKey: imgObjectKey
      };
      debug.value += `\nSending payload to backend: ${JSON.stringify(payload, null, 2)}`;

      const inferRes = await makeSecureRequest(`${apiUrl}/inferences/generateInference`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
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
      debug.value += `\nInference data: ${JSON.stringify(inferData, null, 2)}`;
      
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