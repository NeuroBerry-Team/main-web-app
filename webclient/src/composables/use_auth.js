import { ref, computed } from 'vue';
import { useCSRF } from './use_csrf.js';

// Global authentication state
const isLoggedIn = ref(false);
const user = ref(null);
const loading = ref(false);
const error = ref('');

export function useAuth() {
  const apiUrl = import.meta.env.VITE_API_BASE_URL;
  const { makeSecureRequest, initializeCSRF } = useCSRF();

  // Check if user is logged in
  async function checkAuthStatus() {
    loading.value = true;
    error.value = '';

    try {
      const response = await fetch(`${apiUrl}/auth/isLoggedIn`, {
        method: 'GET',
        credentials: 'include'
      });

      // Handle both successful responses and 401 (unauthorized) as normal cases
      if (response.ok) {
        const data = await response.json();
        if (data.loggedIn) {
          isLoggedIn.value = true;
          // Optionally get user details
          await getUserDetails();
        } else {
          isLoggedIn.value = false;
          user.value = null;
        }
      } else if (response.status === 401) {
        // 401 is expected when not logged in - not an error
        isLoggedIn.value = false;
        user.value = null;
      } else {
        // Other status codes (500, etc.) are actual errors
        console.error(`Auth check failed with status: ${response.status}`);
        isLoggedIn.value = false;
        user.value = null;
        error.value = `Authentication check failed (${response.status})`;
      }
    } catch (err) {
      // Network errors, etc.
      console.error('Auth check network error:', err);
      isLoggedIn.value = false;
      user.value = null;
      error.value = 'Could not verify authentication status';
    } finally {
      loading.value = false;
    }

    return isLoggedIn.value;
  }

  // Get user details (role, etc.)
  async function getUserDetails() {
    try {
      const response = await fetch(`${apiUrl}/auth/getUserRole`, {
        method: 'GET',
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        user.value = { role: data.role };
      }
    } catch (err) {
      console.error('Error getting user details:', err);
    }
  }

  // Logout function
  async function logout() {
    loading.value = true;
    error.value = '';

    try {
      const response = await makeSecureRequest(`${apiUrl}/auth/logout`, {
        method: 'POST'
      });

      if (response.ok) {
        isLoggedIn.value = false;
        user.value = null;
        // Redirect to login
        window.location.href = '/login';
      } else {
        throw new Error('Logout failed');
      }
    } catch (err) {
      console.error('Logout error:', err);
      error.value = 'Logout failed';
      // Even if logout fails on server, clear local state
      isLoggedIn.value = false;
      user.value = null;
    } finally {
      loading.value = false;
    }
  }

  // Computed properties
  const isAdmin = computed(() => {
    return user.value?.role === 'ADMIN' || user.value?.role === 'SUPERADMIN';
  });

  const isAuthenticated = computed(() => isLoggedIn.value);

  return {
    // State
    isLoggedIn: isAuthenticated,
    user,
    loading,
    error,
    
    // Computed
    isAdmin,
    
    // Methods
    checkAuthStatus,
    getUserDetails,
    logout
  };
}
