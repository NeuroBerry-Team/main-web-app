import { ref } from 'vue';
import { useCSRF } from './use_csrf.js';

export function useMetrics() {
  const apiUrl = import.meta.env.VITE_API_BASE_URL;
  const { makeSecureRequest } = useCSRF();

  const loading = ref(false);
  const error = ref('');
  
  // Class detection metrics
  const classDetectionMetrics = ref(null);
  const timeSeriesMetrics = ref(null);
  const summaryMetrics = ref(null);

  /**
   * Get class detection counts across all inferences
   */
  async function getClassDetectionMetrics() {
    loading.value = true;
    error.value = '';

    try {
      const response = await makeSecureRequest(`${apiUrl}/metrics/class-detections`, {
        method: 'GET'
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error fetching class detection metrics');
      }

      if (data.success) {
        classDetectionMetrics.value = data;
      }

      return data;
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching class detection metrics:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Get time series metrics
   * @param {string} grouping - 'day', 'week', or 'month'
   * @param {number} days - Number of days to look back
   */
  async function getTimeSeriesMetrics(grouping = 'day', days = 30) {
    loading.value = true;
    error.value = '';

    try {
      const response = await makeSecureRequest(
        `${apiUrl}/metrics/time-series?grouping=${grouping}&days=${days}`,
        {
          method: 'GET'
        }
      );

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error fetching time series metrics');
      }

      if (data.success) {
        timeSeriesMetrics.value = data;
      }

      return data;
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching time series metrics:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Get summary metrics
   */
  async function getSummaryMetrics() {
    loading.value = true;
    error.value = '';

    try {
      const response = await makeSecureRequest(`${apiUrl}/metrics/summary`, {
        method: 'GET'
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error fetching summary metrics');
      }

      if (data.success) {
        summaryMetrics.value = data;
      }

      return data;
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching summary metrics:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Get class label for a class ID
   */
  function getClassLabel(classId) {
    const classLabels = {
      0: 'C1 Boton',
      1: 'C4 BrightRed',
      2: 'C5 DarkRed',
      3: 'C2 Green',
      4: 'C3 Orange (Red dot)'
    };
    return classLabels[classId] || `Class ${classId}`;
  }

  /**
   * Get color for a class ID
   */
  function getClassColor(classId) {
    const classColors = {
      0: '#6B7280',
      1: '#EF4444',
      2: '#991B1B',
      3: '#22C55E',
      4: '#F59E0B'
    };
    return classColors[classId] || '#6366F1';
  }

  return {
    // State
    loading,
    error,
    classDetectionMetrics,
    timeSeriesMetrics,
    summaryMetrics,

    // Methods
    getClassDetectionMetrics,
    getTimeSeriesMetrics,
    getSummaryMetrics,
    getClassLabel,
    getClassColor
  };
}
