import { ref } from 'vue';

export function useInference() {
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
      debug.value += '\nSolicitando presigned URL...';
      const presignedRes = await fetch(`${apiUrl}/inferences/getBaseImgPresignedUrls`);
      debug.value += `\nRespuesta presigned: status ${presignedRes.status}`;
      if (!presignedRes.ok) throw new Error('Error obteniendo URL de subida');

      const presignedText = await presignedRes.text();
      debug.value += `\nRespuesta presigned (raw): ${presignedText}`;
      let uploadURL, liveURL, imgObjectKey;
      try {
        ({ uploadURL, liveURL, imgObjectKey } = JSON.parse(presignedText));
      } catch (e) {
        throw new Error('Respuesta del backend no es JSON válido');
      }

      debug.value += '\nSubiendo imagen a MinIO...';
      const uploadRes = await fetch(uploadURL, {
        method: 'PUT',
        body: selectedFile,
        headers: { 'Content-Type': selectedFile.type }
      });
      debug.value += `\nRespuesta subida: status ${uploadRes.status}`;
      if (!uploadRes.ok) throw new Error('Error subiendo imagen a MinIO');

      const payload = {
        name: selectedFile.name,
        imgUrl: liveURL,
        imgObjectKey: imgObjectKey
      };
      debug.value += `\nEnviando payload a backend: ${JSON.stringify(payload, null, 2)}`;

      const inferRes = await fetch(`${apiUrl}/inferences/generateInference`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      debug.value += `\nRespuesta inferencia: status ${inferRes.status}`;
      if (!inferRes.ok) throw new Error('Error generando inferencia');
      const inferData = await inferRes.json();
      result.value = inferData;
      debug.value += `\nDatos inferencia: ${JSON.stringify(inferData, null, 2)}`;
    } catch (err) {
      error.value = err.message;
      debug.value += `\nError: ${err.message}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  return { loading, error, result, debug, handleInference };
}