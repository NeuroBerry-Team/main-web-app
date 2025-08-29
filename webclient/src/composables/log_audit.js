import { useCSRF } from './use_csrf.js'

export const useAudit = () => {
  const { makeSecureRequest } = useCSRF()
  const apiUrl = import.meta.env.VITE_API_BASE_URL

  const logAuditAction = async (action, entityType, entityId = null, details = {}) => {
    try {
      await makeSecureRequest(`${apiUrl}/audit/log`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action,
          entityType,
          entityId,
          details
        })
      })
    } catch (err) {
      console.warn('Failed to log audit action:', err)
      // Don't throw error as this shouldn't block the main operation
    }
  }

  const logModelTraining = async (modelName, datasetId, modelType, modelId = null) => {
    await logAuditAction('MODEL_TRAINING_STARTED', 'MODEL', modelId, {
      modelName,
      datasetId,
      modelType
    })
  }

  const logDatasetAction = async (action, datasetId, datasetName = null, additionalDetails = {}) => {
    await logAuditAction(action, 'DATASET', datasetId, {
      datasetName,
      ...additionalDetails
    })
  }

  const logInferenceAction = async (action, inferenceId = null, details = {}) => {
    await logAuditAction(action, 'INFERENCE', inferenceId, details)
  }

  const logUserAction = async (action, userId = null, details = {}) => {
    await logAuditAction(action, 'USER', userId, details)
  }

  return {
    logAuditAction,
    logModelTraining,
    logDatasetAction,
    logInferenceAction,
    logUserAction
  }
}
