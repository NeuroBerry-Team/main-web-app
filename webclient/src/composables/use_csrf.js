import { ref } from 'vue'

// Global CSRF token state
const csrfToken = ref('')

export function useCSRF() {
  const apiUrl = import.meta.env.VITE_API_BASE_URL

    // Function to fetch CSRF token from the server
  async function fetchCSRFToken() {
    try {
      const response = await fetch(`${apiUrl}/auth/csrf-token`, {
        method: 'GET',
        credentials: 'include'
      })

      if (response.ok) {
        const data = await response.json()
        csrfToken.value = data.csrf_token
      } else {
        console.error('Failed to fetch CSRF token')
        csrfToken.value = null
      }
    } catch (error) {
      console.error('Failed to fetch CSRF token', error)
      csrfToken.value = null
    }
  }

  // Function to make secure requests with CSRF token
  async function makeSecureRequest(url, options = {}) {
    // Ensure we have a CSRF token
    if (!csrfToken.value) {
      await fetchCSRFToken()
    }

    // Add CSRF token to headers
    if (csrfToken.value) {
      options.headers = {
        ...options.headers,
        'X-CSRF-Token': csrfToken.value
      }
    }

    // Ensure credentials are included
    options.credentials = 'include'

    try {
      const response = await fetch(url, options)
      
      // If CSRF token is invalid, try to refresh it once
      if (response.status === 403) {
        const errorText = await response.text()
        
        if (errorText.includes('CSRF') || errorText.includes('csrf')) {
          await fetchCSRFToken()
          
          // Retry the request with new token
          if (csrfToken.value) {
            options.headers = {
              ...options.headers,
              'X-CSRF-Token': csrfToken.value
            }
            const retryResponse = await fetch(url, options)
            return retryResponse
          }
        }
      }

      return response
    } catch (error) {
      console.error('Secure request failed:', error)
      throw error
    }
  }

  // Initialize CSRF token on first load
  async function initializeCSRF() {
    await fetchCSRFToken()
  }

  return {
    csrfToken,
    fetchCSRFToken,
    makeSecureRequest,
    initializeCSRF
  }
}
