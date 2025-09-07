import { ref, computed } from 'vue'

export function useMinioMetadata() {
  const loading = ref(false)
  const error = ref(null)
  const metadata = ref(null)
  const detectedBoxes = ref([])
  
  // Cache for storing metadata to avoid repeated requests
  const metadataCache = ref(new Map())
  const metadataLoaded = ref(new Set())
  
  // Confidence calculation cache
  const confidenceCache = ref(new Map())

  /**
   * Fetch metadata from Minio for a specific inference
   * @param {string|number} inferenceId - The ID of the inference
   * @param {boolean} forceRefresh - Whether to force refresh even if cached
   * @returns {Promise<Object|null>} - The metadata object or null if failed
   */
  const fetchMetadata = async (inferenceId, forceRefresh = false) => {
    if (!inferenceId) {
      error.value = 'Inference ID is required'
      return null
    }

    // Check cache first (unless force refresh)
    if (!forceRefresh && metadataCache.value.has(inferenceId)) {
      const cachedData = metadataCache.value.get(inferenceId)
      metadata.value = cachedData
      processMetadata(cachedData, inferenceId)
      return cachedData
    }

    loading.value = true
    error.value = null

    try {
      const apiUrl = import.meta.env.VITE_API_BASE_URL
      const response = await fetch(`${apiUrl}/inferences/getInferenceMetadata/${inferenceId}`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (data.success && data.metadata) {
        // Cache the metadata
        metadataCache.value.set(inferenceId, data.metadata)
        metadataLoaded.value.add(inferenceId)
        
        metadata.value = data.metadata
        processMetadata(data.metadata, inferenceId)
        
        return data.metadata
      } else {
        throw new Error(data.error || 'Failed to load metadata')
      }
    } catch (err) {
      console.error('Error fetching metadata from Minio:', err)
      error.value = err.message
      
      // Mark as loaded even on error to prevent infinite retries
      metadataLoaded.value.add(inferenceId)
      
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Process metadata and extract detected boxes
   * @param {Object} metadataObj - The metadata object
   * @param {string|number} inferenceId - The inference ID
   */
  const processMetadata = (metadataObj, inferenceId) => {
    if (!metadataObj || !metadataObj.detections) {
      detectedBoxes.value = []
      return
    }

    // Calculate and cache average confidence
    calculateAverageConfidence(inferenceId, metadataObj.detections)

    // Get original image dimensions from metadata
    const imageInfo = metadataObj.image_info
    const originalImageSize = imageInfo ? imageInfo.original_size : null

    // Map the detections to detectedBoxes format
    detectedBoxes.value = metadataObj.detections.map((detection, index) => {
      // Use normalized coordinates directly from YOLO if available
      let normalizedBbox = null
      
      if (detection.bbox_normalized) {
        // Use the normalized coordinates provided by YOLO (preferred method)
        normalizedBbox = detection.bbox_normalized
      } else if (originalImageSize && detection.bbox) {
        // Fallback: manually normalize if only pixel coordinates available
        normalizedBbox = normalizeCoordinates(detection.bbox, originalImageSize)
      } else {
        normalizedBbox = null
      }

      return {
        id: `${inferenceId}-${index}`,
        class_id: detection.class_id,
        label: getClassLabel(detection.class_id),
        confidence: detection.confidence,
        bbox_normalized: normalizedBbox,
        bbox_original: detection.bbox,
        color: getBoxColor(detection.class_id),
        visible: true,
        originalImageSize: originalImageSize
      }
    })
  }

  /**
   * Calculate and cache average confidence from detections
   * @param {string|number} inferenceId - The inference ID
   * @param {Array} detections - Array of detection objects
   * @returns {number|null} - Average confidence or null
   */
  const calculateAverageConfidence = (inferenceId, detections) => {
    if (!detections || detections.length === 0) {
      confidenceCache.value.set(inferenceId, null)
      return null
    }

    const totalConfidence = detections.reduce((sum, detection) => sum + detection.confidence, 0)
    const averageConfidence = totalConfidence / detections.length

    // Cache the result
    confidenceCache.value.set(inferenceId, averageConfidence)

    return averageConfidence
  }

  /**
   * Get cached confidence for an inference
   * @param {string|number} inferenceId - The inference ID
   * @returns {number|null} - Cached confidence or null
   */
  const getCachedConfidence = (inferenceId) => {
    return confidenceCache.value.get(inferenceId) || null
  }

  /**
   * Normalize bounding box coordinates to 0-1 range
   * @param {Object|Array} bbox - Bounding box coordinates
   * @param {Array} imageSize - [width, height] of the original image
   * @returns {Object|null} - Normalized coordinates or null
   */
  const normalizeCoordinates = (bbox, imageSize) => {
    const [imageWidth, imageHeight] = imageSize

    let x1, y1, x2, y2

    if (Array.isArray(bbox)) {
      [x1, y1, x2, y2] = bbox
    } else if (bbox && typeof bbox === 'object') {
      ({ x1, y1, x2, y2 } = bbox)
    } else {
      console.error('Invalid bbox format:', bbox)
      return null
    }

    // Ensure x1 < x2 and y1 < y2
    let nx1 = x1 / imageWidth
    let ny1 = y1 / imageHeight
    let nx2 = x2 / imageWidth
    let ny2 = y2 / imageHeight

    // Clamp to [0,1]
    nx1 = Math.max(0, Math.min(1, nx1))
    ny1 = Math.max(0, Math.min(1, ny1))
    nx2 = Math.max(0, Math.min(1, nx2))
    ny2 = Math.max(0, Math.min(1, ny2))

    // Swap if needed
    if (nx1 > nx2) [nx1, nx2] = [nx2, nx1]
    if (ny1 > ny2) [ny1, ny2] = [ny2, ny1]

    // Avoid zero-area boxes
    if (Math.abs(nx2 - nx1) < 1e-6 || Math.abs(ny2 - ny1) < 1e-6) {
      return null
    }

    return { x1: nx1, y1: ny1, x2: nx2, y2: ny2 }
  }

  /**
   * Get class label for a class ID
   * @param {number} classId - The class ID
   * @returns {string} - The class label
   */
  const getClassLabel = (classId) => {
    const classLabels = {
      2: 'C5 DarkRed',
      1: 'C4 BrightRed',
      4: 'C3 Orange (Red dot)',
      3: 'C2 Green',
      0: 'C1 Boton',
    }
    return classLabels[classId] || `Clase ${classId}`
  }

  /**
   * Get all class labels
   * @returns {Object} - Object mapping class IDs to labels
   */
  const getAllClassLabels = () => {
    return {
      2: 'C5 DarkRed',
      1: 'C4 BrightRed',
      4: 'C3 Orange (Red dot)',
      3: 'C2 Green',
      0: 'C1 Boton'
    }
  }

  /**
   * Get color for a class ID
   * @param {number} classId - The class ID
   * @returns {string} - The color hex code
   */
  const getBoxColor = (classId) => {
    const classColors = {
      2: '#991B1B', // C5 DarkRed
      1: '#EF4444', // C4 BrightRed
      4: '#F59E0B', // C3 Orange
      3: '#22C55E', // C2 Green
      0: '#6B7280', // C1 Boton (gray)
    }
    return classColors[classId] || '#6366F1' // Default purple color
  }

  /**
   * Check if metadata is loaded for an inference
   * @param {string|number} inferenceId - The inference ID
   * @returns {boolean} - Whether metadata is loaded
   */
  const isMetadataLoaded = (inferenceId) => {
    return metadataLoaded.value.has(inferenceId)
  }

  /**
   * Get class count summary from detected boxes
   * @returns {Object|null} - Object with class counts or null
   */
  const classCountSummary = computed(() => {
    if (!detectedBoxes.value || detectedBoxes.value.length === 0) {
      return null
    }

    // Initialize all classes with 0
    const allClasses = getAllClassLabels()
    const counts = {}

    Object.values(allClasses).forEach(label => {
      counts[label] = 0
    })

    // Count detected boxes by their actual labels
    detectedBoxes.value.forEach(box => {
      const label = box.label || getClassLabel(box.class_id)
      if (label && counts.hasOwnProperty(label)) {
        counts[label] += 1
      }
    })

    return counts
  })

  /**
   * Clear metadata for a specific inference or all
   * @param {string|number} inferenceId - Optional specific inference ID to clear
   */
  const clearMetadata = (inferenceId = null) => {
    if (inferenceId) {
      metadataCache.value.delete(inferenceId)
      metadataLoaded.value.delete(inferenceId)
      confidenceCache.value.delete(inferenceId)
    } else {
      metadataCache.value.clear()
      metadataLoaded.value.clear()
      confidenceCache.value.clear()
    }
    
    metadata.value = null
    detectedBoxes.value = []
    error.value = null
  }

  return {
    // State
    loading,
    error,
    metadata,
    detectedBoxes,
    
    // Computed
    classCountSummary,
    
    // Methods
    fetchMetadata,
    getCachedConfidence,
    isMetadataLoaded,
    clearMetadata,
    
    // Utility functions
    getClassLabel,
    getAllClassLabels,
    getBoxColor,
    normalizeCoordinates
  }
}
