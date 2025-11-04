<template>
  <div class="user-management">
    <div class="header-section">
      <h2 class="section-title">Gestión de Usuarios</h2>
      <button @click="showCreateModal = true" class="btn-primary">
        <span class="icon">➕</span> Nuevo Usuario
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !users.length" class="loading-container">
      <div class="spinner"></div>
      <p>Cargando usuarios...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <p class="error-message">⚠️ {{ error }}</p>
      <button @click="loadUsers" class="btn-secondary">Reintentar</button>
    </div>

    <!-- Users Table -->
    <div v-else class="table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Análisis</th>
            <th>Último Acceso</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" class="user-row">
            <td>{{ user.id }}</td>
            <td>{{ user.name }} {{ user.lastName }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span class="role-badge" :class="`role-${user.role.name.toLowerCase()}`">
                {{ getRoleLabel(user.role.name) }}
              </span>
            </td>
            <td>{{ user.inferenceCount || 0 }}</td>
            <td>{{ formatDate(user.lastLogin) }}</td>
            <td class="actions-cell">
              <button 
                @click="openEditModal(user)" 
                class="btn-icon btn-edit"
                title="Editar rol"
              >
                ✏️
              </button>
              <button 
                @click="confirmDelete(user)" 
                class="btn-icon btn-delete"
                :disabled="user.role.name === 'SUPERADMIN'"
                title="Eliminar usuario"
              >
                🗑️
              </button>
              <button 
                @click="viewUserStats(user)" 
                class="btn-icon btn-info"
                title="Ver estadísticas"
              >
                📊
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!users.length" class="empty-state">
        <p>No hay usuarios registrados</p>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Crear Nuevo Usuario</h3>
          <button @click="closeCreateModal" class="btn-close">✕</button>
        </div>
        <form @submit.prevent="handleCreateUser" class="modal-body">
          <div class="form-group">
            <label>Nombre</label>
            <input 
              v-model="newUser.name" 
              type="text" 
              required 
              placeholder="Nombre del usuario"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>Apellido</label>
            <input 
              v-model="newUser.lastName" 
              type="text" 
              required 
              placeholder="Apellido del usuario"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input 
              v-model="newUser.email" 
              type="email" 
              required 
              placeholder="correo@ejemplo.com"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>Contraseña</label>
            <input 
              v-model="newUser.passwd" 
              type="password" 
              required 
              placeholder="Mínimo 8 caracteres"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>Rol</label>
            <select v-model="newUser.roleId" required class="form-select">
              <option value="">Selecciona un rol</option>
              <option v-for="role in availableRoles" :key="role.id" :value="role.id">
                {{ getRoleLabel(role.name) }}
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeCreateModal" class="btn-secondary">
              Cancelar
            </button>
            <button type="submit" class="btn-primary" :disabled="creatingUser">
              {{ creatingUser ? 'Creando...' : 'Crear Usuario' }}
            </button>
          </div>
          <div v-if="createError" class="error-message">
            {{ createError }}
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Role Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Editar Rol de Usuario</h3>
          <button @click="closeEditModal" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <p class="user-info">
            <strong>{{ editingUser.name }} {{ editingUser.lastName }}</strong><br>
            {{ editingUser.email }}
          </p>
          <div class="form-group">
            <label>Nuevo Rol</label>
            <select v-model="editingUser.newRoleId" required class="form-select">
              <option v-for="role in availableRoles" :key="role.id" :value="role.id">
                {{ getRoleLabel(role.name) }}
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeEditModal" class="btn-secondary">
              Cancelar
            </button>
            <button @click="handleUpdateRole" class="btn-primary" :disabled="updatingRole">
              {{ updatingRole ? 'Actualizando...' : 'Actualizar Rol' }}
            </button>
          </div>
          <div v-if="editError" class="error-message">
            {{ editError }}
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-content modal-danger">
        <div class="modal-header">
          <h3>⚠️ Confirmar Eliminación</h3>
          <button @click="closeDeleteModal" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <p class="warning-text">
            ¿Estás seguro de que deseas eliminar al usuario?
          </p>
          <p class="user-info">
            <strong>{{ deletingUser.name }} {{ deletingUser.lastName }}</strong><br>
            {{ deletingUser.email }}
          </p>
          <p class="warning-text">
            Esta acción no se puede deshacer y se eliminarán todos los datos asociados al usuario.
          </p>
          <div class="modal-actions">
            <button type="button" @click="closeDeleteModal" class="btn-secondary">
              Cancelar
            </button>
            <button @click="handleDeleteUser" class="btn-danger" :disabled="deletingUserLoading">
              {{ deletingUserLoading ? 'Eliminando...' : 'Eliminar Usuario' }}
            </button>
          </div>
          <div v-if="deleteError" class="error-message">
            {{ deleteError }}
          </div>
        </div>
      </div>
    </div>

    <!-- User Stats Modal -->
    <div v-if="showStatsModal" class="modal-overlay" @click.self="closeStatsModal">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>📊 Estadísticas del Usuario</h3>
          <button @click="closeStatsModal" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingStats" class="loading-container">
            <div class="spinner"></div>
            <p>Cargando estadísticas...</p>
          </div>
          <div v-else-if="userStats" class="stats-grid">
            <div class="stat-card">
              <div class="stat-value">{{ userStats.totalAnalyses || 0 }}</div>
              <div class="stat-label">Total de Análisis</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ userStats.analysesThisWeek || 0 }}</div>
              <div class="stat-label">Esta Semana</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ userStats.activeDays || 0 }}</div>
              <div class="stat-label">Días Activos</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ userStats.loginStreak || 0 }}</div>
              <div class="stat-label">Racha de Accesos</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdmin } from '../../composables/use_admin.js';

const { users, loading, error, getAllUsers, createUser, updateUserRole, deleteUser, getUserStatistics } = useAdmin();

// Modals
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const showStatsModal = ref(false);

// Form states
const newUser = ref({
  name: '',
  lastName: '',
  email: '',
  passwd: '',
  roleId: ''
});

const editingUser = ref({});
const deletingUser = ref({});
const userStats = ref(null);

const creatingUser = ref(false);
const updatingRole = ref(false);
const deletingUserLoading = ref(false);
const loadingStats = ref(false);
const createError = ref('');
const editError = ref('');
const deleteError = ref('');

// Available roles (hardcoded for now, can be fetched from API)
const availableRoles = ref([
  { id: 1, name: 'SUPERADMIN' },
  { id: 2, name: 'ADMIN' },
  { id: 3, name: 'AI_USER' }
]);

// Load users on mount
onMounted(async () => {
  await loadUsers();
});

async function loadUsers() {
  try {
    await getAllUsers();
  } catch (err) {
    console.error('Error loading users:', err);
  }
}

// Create user handlers
function closeCreateModal() {
  showCreateModal.value = false;
  newUser.value = {
    name: '',
    lastName: '',
    email: '',
    passwd: '',
    roleId: ''
  };
  createError.value = '';
}

async function handleCreateUser() {
  creatingUser.value = true;
  createError.value = '';
  
  try {
    await createUser(newUser.value);
    closeCreateModal();
  } catch (err) {
    createError.value = err.message;
  } finally {
    creatingUser.value = false;
  }
}

// Edit role handlers
function openEditModal(user) {
  editingUser.value = {
    id: user.id,
    name: user.name,
    lastName: user.lastName,
    email: user.email,
    currentRoleId: user.role.id,
    newRoleId: user.role.id
  };
  editError.value = '';
  showEditModal.value = true;
}

function closeEditModal() {
  showEditModal.value = false;
  editingUser.value = {};
  editError.value = '';
}

async function handleUpdateRole() {
  if (editingUser.value.newRoleId === editingUser.value.currentRoleId) {
    closeEditModal();
    return;
  }

  updatingRole.value = true;
  editError.value = '';
  
  try {
    await updateUserRole(editingUser.value.id, editingUser.value.newRoleId);
    closeEditModal();
  } catch (err) {
    editError.value = err.message;
    console.error('Error updating role:', err);
  } finally {
    updatingRole.value = false;
  }
}

// Delete user handlers
function confirmDelete(user) {
  if (user.role.name === 'SUPERADMIN') {
    alert('No se puede eliminar un usuario SUPERADMIN');
    return;
  }
  
  deletingUser.value = {
    id: user.id,
    name: user.name,
    lastName: user.lastName,
    email: user.email
  };
  deleteError.value = '';
  showDeleteModal.value = true;
}

function closeDeleteModal() {
  showDeleteModal.value = false;
  deletingUser.value = {};
  deleteError.value = '';
}

async function handleDeleteUser() {
  deletingUserLoading.value = true;
  deleteError.value = '';
  
  try {
    await deleteUser(deletingUser.value.id);
    closeDeleteModal();
  } catch (err) {
    deleteError.value = err.message;
    console.error('Error deleting user:', err);
  } finally {
    deletingUserLoading.value = false;
  }
}

// Stats handlers
async function viewUserStats(user) {
  userStats.value = null;
  showStatsModal.value = true;
  loadingStats.value = true;
  
  try {
    const stats = await getUserStatistics(user.id);
    userStats.value = stats;
  } catch (err) {
    console.error('Error loading stats:', err);
  } finally {
    loadingStats.value = false;
  }
}

function closeStatsModal() {
  showStatsModal.value = false;
  userStats.value = null;
}

// Utility functions
function getRoleLabel(roleName) {
  const roleLabels = {
    'SUPERADMIN': 'Super Administrador',
    'ADMIN': 'Administrador',
    'AI_USER': 'Usuario'
  };
  return roleLabels[roleName] || roleName;
}

function formatDate(dateString) {
  if (!dateString) return 'Nunca';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Hoy';
  if (diffDays === 1) return 'Ayer';
  if (diffDays < 7) return `Hace ${diffDays} días`;
  
  return date.toLocaleDateString('es-ES', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
}
</script>

<style scoped>
.user-management {
  width: 100%;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #b91c1c;
  margin: 0;
}

/* Buttons */
.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #b91c1c;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background-color: #991b1b;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(185, 28, 28, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background-color: #e5e7eb;
  color: #374151;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background-color: #d1d5db;
}

.btn-danger {
  padding: 0.75rem 1.5rem;
  background-color: #dc2626;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-danger:hover {
  background-color: #b91c1c;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  padding: 0.5rem;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.btn-edit:hover {
  background-color: #dbeafe;
}

.btn-delete:hover:not(:disabled) {
  background-color: #fee2e2;
}

.btn-delete:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.btn-info:hover {
  background-color: #f3e8ff;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.2s;
}

.btn-close:hover {
  color: #b91c1c;
}

/* Loading and Error States */
.loading-container,
.error-container {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f4f6;
  border-top-color: #b91c1c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  color: #dc2626;
  font-weight: 600;
  margin-bottom: 1rem;
}

/* Table */
.table-container {
  overflow-x: auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table thead {
  background-color: #f9fafb;
  border-bottom: 2px solid #e5e7eb;
}

.users-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.users-table tbody tr {
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s;
}

.users-table tbody tr:hover {
  background-color: #f9fafb;
}

.users-table td {
  padding: 1rem;
  color: #1f2937;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.role-superadmin {
  background-color: #fef3c7;
  color: #92400e;
}

.role-admin {
  background-color: #dbeafe;
  color: #1e40af;
}

.role-ai_user {
  background-color: #d1fae5;
  color: #065f46;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-size: 1.1rem;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.modal-large {
  max-width: 700px;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.modal-body {
  padding: 1.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.modal-danger .modal-header h3 {
  color: #dc2626;
}

/* Form Elements */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #b91c1c;
  box-shadow: 0 0 0 3px rgba(185, 28, 28, 0.1);
}

.user-info {
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.warning-text {
  color: #dc2626;
  font-weight: 500;
  margin-bottom: 1rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-card {
  padding: 1.5rem;
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #b91c1c;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .table-container {
    overflow-x: scroll;
  }

  .users-table {
    min-width: 800px;
  }

  .modal-content {
    width: 95%;
    margin: 1rem;
  }
}
</style>
