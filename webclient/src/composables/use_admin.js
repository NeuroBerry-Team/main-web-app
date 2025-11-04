import { ref } from 'vue';
import { useCSRF } from './use_csrf.js';

export function useAdmin() {
  const apiUrl = import.meta.env.VITE_API_BASE_URL;
  const { makeSecureRequest } = useCSRF();

  const users = ref([]);
  const roles = ref([]);
  const loading = ref(false);
  const error = ref('');

  async function getAllUsers() {
    loading.value = true;
    error.value = '';

    try {
      const response = await makeSecureRequest(`${apiUrl}/admin/users`, {
        method: 'GET'
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('No autorizado. Por favor inicia sesión.');
        } else if (response.status === 403) {
          throw new Error('Acceso denegado. No tienes permisos de administrador.');
        } else {
          throw new Error(`Error al obtener usuarios: ${response.status}`);
        }
      }

      const data = await response.json();
      
      if (data.success && data.users) {
        users.value = data.users;
      } else {
        throw new Error('Formato de respuesta inválido');
      }

      return data.users;
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching users:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function getRoles() {
    loading.value = true;
    error.value = '';

    try {
      const response = await makeSecureRequest(`${apiUrl}/admin/roles`, {
        method: 'GET'
      });

      if (!response.ok) {
        throw new Error(`Error al obtener roles: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.roles) {
        roles.value = data.roles;
      }

      return data.roles;
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching roles:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createUser(userData) {
    loading.value = true;
    error.value = '';

    try {
      const response = await makeSecureRequest(`${apiUrl}/auth/addUser`, {
        method: 'POST',
        body: JSON.stringify(userData)
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error al crear usuario');
      }
      
      // Refresh users list
      await getAllUsers();
      
      return data;
    } catch (err) {
      error.value = err.message;
      console.error('Error creating user:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateUserRole(userId, newRoleId) {
    loading.value = true;
    error.value = '';

    try {
      const response = await makeSecureRequest(`${apiUrl}/admin/users/${userId}/role`, {
        method: 'PUT',
        body: JSON.stringify({ roleId: newRoleId })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error al actualizar rol');
      }
      
      // Refresh users list
      await getAllUsers();
      
      return data;
    } catch (err) {
      error.value = err.message;
      console.error('Error updating user role:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteUser(userId) {
    loading.value = true;
    error.value = '';

    try {
      const response = await makeSecureRequest(`${apiUrl}/admin/users/${userId}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error al eliminar usuario');
      }
      
      // Refresh users list
      await getAllUsers();
      
      return data;
    } catch (err) {
      error.value = err.message;
      console.error('Error deleting user:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function getUserStatistics(userId) {
    loading.value = true;
    error.value = '';

    try {
      const response = await makeSecureRequest(`${apiUrl}/admin/users/${userId}/stats`, {
        method: 'GET'
      });

      if (!response.ok) {
        throw new Error(`Error al obtener estadísticas: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      error.value = err.message;
      console.error('Error fetching user statistics:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    // State
    users,
    roles,
    loading,
    error,

    // Methods
    getAllUsers,
    getRoles,
    createUser,
    updateUserRole,
    deleteUser,
    getUserStatistics
  };
}
