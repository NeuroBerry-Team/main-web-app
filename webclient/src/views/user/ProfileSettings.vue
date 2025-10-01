<template>
  <div class="page-wrapper">
    <header class="page-header animated-item">
      <div>
        <h1 class="section-title">Configuración de Cuenta</h1>
        <p class="section-text">Gestiona tu información personal y de seguridad.</p>
      </div>
      <router-link to="/profile" class="action-btn btn-secondary">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
        <span>Volver al Perfil</span>
      </router-link>
    </header>

    <div class="settings-content">
      <section class="content-section animated-item" style="animation-delay: 0.1s;">
        <h2 class="subsection-title">Información Personal</h2>
        <p class="subsection-description">Actualiza tu nombre y correo electrónico.</p>
        <form @submit.prevent="updatePersonalInfo" class="settings-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="firstName" class="form-label">Nombre *</label>
              <input id="firstName" v-model="personalForm.name" type="text" required class="form-input" :class="{'is-invalid': personalFormErrors.name}" @input="clearFieldError('personal', 'name')" />
              <p v-if="personalFormErrors.name" class="error-text">{{ personalFormErrors.name }}</p>
            </div>
            <div class="form-group">
              <label for="lastName" class="form-label">Apellido *</label>
              <input id="lastName" v-model="personalForm.lastName" type="text" required class="form-input" :class="{'is-invalid': personalFormErrors.lastName}" @input="clearFieldError('personal', 'lastName')" />
              <p v-if="personalFormErrors.lastName" class="error-text">{{ personalFormErrors.lastName }}</p>
            </div>
          </div>
          <div class="form-group">
            <label for="email" class="form-label">Correo Electrónico *</label>
            <input id="email" v-model="personalForm.email" type="email" required class="form-input" :class="{'is-invalid': personalFormErrors.email}" @input="clearFieldError('personal', 'email')" />
            <p v-if="personalFormErrors.email" class="error-text">{{ personalFormErrors.email }}</p>
          </div>
          <div class="form-actions">
            <button type="submit" :disabled="personalFormLoading" class="action-btn btn-primary">
              <span v-if="personalFormLoading" class="spinner"></span>
              {{ personalFormLoading ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </div>
        </form>
      </section>

      <section class="content-section animated-item" style="animation-delay: 0.2s;">
        <h2 class="subsection-title">Cambiar Contraseña</h2>
        <p class="subsection-description">Mantén tu cuenta segura actualizando tu contraseña regularmente.</p>
        <form @submit.prevent="changePassword" class="settings-form">
           <div class="form-group">
              <label for="currentPassword" class="form-label">Contraseña Actual *</label>
              <input id="currentPassword" v-model="passwordForm.currentPassword" type="password" required class="form-input" :class="{'is-invalid': passwordFormErrors.currentPassword}" @input="clearFieldError('password', 'currentPassword')" />
              <p v-if="passwordFormErrors.currentPassword" class="error-text">{{ passwordFormErrors.currentPassword }}</p>
            </div>
          <div class="form-grid">
            <div class="form-group">
              <label for="newPassword" class="form-label">Nueva Contraseña *</label>
              <input id="newPassword" v-model="passwordForm.newPassword" type="password" required class="form-input" :class="{'is-invalid': passwordFormErrors.newPassword}" @input="clearFieldError('password', 'newPassword')" />
              <p v-if="passwordFormErrors.newPassword" class="error-text">{{ passwordFormErrors.newPassword }}</p>
            </div>
            <div class="form-group">
              <label for="confirmPassword" class="form-label">Confirmar Nueva Contraseña *</label>
              <input id="confirmPassword" v-model="passwordForm.confirmPassword" type="password" required class="form-input" :class="{'is-invalid': passwordFormErrors.confirmPassword}" @input="clearFieldError('password', 'confirmPassword')" />
              <p v-if="passwordFormErrors.confirmPassword" class="error-text">{{ passwordFormErrors.confirmPassword }}</p>
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" :disabled="passwordFormLoading" class="action-btn btn-primary">
              <span v-if="passwordFormLoading" class="spinner"></span>
              {{ passwordFormLoading ? 'Cambiando...' : 'Cambiar Contraseña' }}
            </button>
          </div>
        </form>
      </section>

      <section class="content-section danger-zone animated-item" style="animation-delay: 0.3s;">
        <h2 class="subsection-title">Zona de Peligro</h2>
        <div class="danger-item">
          <div>
            <p class="danger-title">Eliminar Cuenta</p>
            <p class="danger-text">Esta acción es permanente y eliminará todos tus datos.</p>
          </div>
          <button @click="showDeleteConfirmation = true" class="action-btn btn-danger">
            Eliminar Cuenta
          </button>
        </div>
      </section>
    </div>

    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="showDeleteConfirmation" class="modal-overlay" @click="showDeleteConfirmation = false">
          <div class="modal-content" @click.stop>
            <div class="modal-icon">⚠️</div>
            <h3 class="modal-title">¿Estás seguro?</h3>
            <p class="modal-text">
              Esta acción eliminará permanentemente tu cuenta y todos los datos asociados. No podrás recuperar esta información.
            </p>
            <div class="modal-actions">
              <button @click="showDeleteConfirmation = false" class="action-btn btn-secondary">Cancelar</button>
              <button @click="deleteAccount" :disabled="deleteLoading" class="action-btn btn-danger">
                <span v-if="deleteLoading" class="spinner"></span>
                {{ deleteLoading ? 'Eliminando...' : 'Sí, Eliminar' }}
              </button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
// --- LÓGICA DEL COMPONENTE (SIN CAMBIOS) ---
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/composables/use_auth.js';
import { useCSRF } from '@/composables/use_csrf.js';
import { useToast } from "vue-toastification";

const router = useRouter();
const { user, checkAuthStatus } = useAuth();
const { makeSecureRequest } = useCSRF();
const toast = useToast();
const apiUrl = import.meta.env.VITE_API_BASE_URL;

const personalForm = reactive({ name: '', lastName: '', email: '' });
const passwordForm = reactive({ currentPassword: '', newPassword: '', confirmPassword: '' });
const personalFormLoading = ref(false);
const passwordFormLoading = ref(false);
const deleteLoading = ref(false);
const personalFormErrors = reactive({ name: '', lastName: '', email: '' });
const passwordFormErrors = reactive({ currentPassword: '', newPassword: '', confirmPassword: '' });
const showDeleteConfirmation = ref(false);

onMounted(async () => {
  await checkAuthStatus();
  if (user.value) {
    personalForm.name = user.value.name || '';
    personalForm.lastName = user.value.lastName || '';
    personalForm.email = user.value.email || '';
  }
});

const clearFieldError = (formType, field) => {
  if (formType === 'personal') personalFormErrors[field] = '';
  if (formType === 'password') passwordFormErrors[field] = '';
};
const updatePersonalInfo = async () => {
  personalFormLoading.value = true;
  try {
    const response = await makeSecureRequest(`${apiUrl}/users/update-profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: personalForm.name, lastName: personalForm.lastName, email: personalForm.email })
    });
    const data = await response.json();
    if (response.ok) {
      toast.success('Información actualizada. La página se recargará.');
      setTimeout(() => window.location.reload(), 2000);
    } else {
      toast.error(data.message || 'Error al actualizar.');
    }
  } catch (error) {
    toast.error('Error de conexión.');
  } finally {
    personalFormLoading.value = false;
  }
};
const changePassword = async () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    toast.error('Las nuevas contraseñas no coinciden.');
    return;
  }
  passwordFormLoading.value = true;
  try {
    const response = await makeSecureRequest(`${apiUrl}/users/change-password`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ currentPassword: passwordForm.currentPassword, newPassword: passwordForm.newPassword })
    });
    const data = await response.json();
    if (response.ok) {
      toast.success('Contraseña cambiada. La página se recargará.');
      setTimeout(() => window.location.reload(), 2000);
    } else {
      toast.error(data.message || 'Error al cambiar la contraseña.');
    }
  } catch (error) {
    toast.error('Error de conexión.');
  } finally {
    passwordFormLoading.value = false;
  }
};
const deleteAccount = async () => {
  deleteLoading.value = true;
  try {
    const response = await makeSecureRequest(`${apiUrl}/users/delete-account`, { method: 'DELETE' });
    if (response.ok) {
      toast.success('Cuenta eliminada. Serás redirigido.');
      setTimeout(() => router.push('/'), 2500);
    } else {
      const data = await response.json();
      toast.error(data.message || 'No se pudo eliminar la cuenta.');
    }
  } catch (error) {
    toast.error('Error de conexión.');
  } finally {
    deleteLoading.value = false;
    showDeleteConfirmation.value = false;
  }
};
</script>

<style scoped>
/* --- ESTILOS VISUALES COHERENTES --- */
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 2rem;
  padding-top: 7rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  background-color: #f8fafc;
}

/* --- Encabezado --- */
.page-header {
  max-width: 1200px;
  margin: 0 auto 2.5rem auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.section-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #b91c1c;
}
.section-text {
  font-size: 1.1rem;
  color: #555;
  margin-top: 0.25rem;
}

/* --- Contenido Principal --- */
.settings-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}
.content-section {
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.07);
  padding: 2.5rem;
  border: 1px solid #e5e7eb;
}
.subsection-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.5rem;
}
.subsection-description {
  color: #6b7280;
  margin-bottom: 2rem;
}

/* --- Formularios --- */
.settings-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.form-label { font-weight: 600; font-size: 0.9rem; color: #444; }
.form-input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-size: 1rem;
}
.form-input:focus {
  outline: none;
  border-color: #b91c1c;
  box-shadow: 0 0 0 3px rgba(178, 34, 34, 0.1);
}
.form-input.is-invalid {
  border-color: #ef4444;
  background-color: #fef2f2;
}
.error-text { font-size: 0.8rem; color: #b91c1c; }
.form-actions { display: flex; justify-content: flex-end; margin-top: 1rem; }

/* --- Zona de Peligro --- */
.danger-zone { border-color: #fecaca; background-color: #fff5f5; }
.danger-zone .subsection-title { color: #991b1b; }
.danger-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.danger-title { font-weight: 600; color: #991b1b; }
.danger-text { color: #b91c1c; font-size: 0.9rem; }

/* --- Botones --- */
.action-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.7rem 1.5rem; border-radius: 8px; font-weight: 600; border: none;
  cursor: pointer; transition: all 0.2s ease; text-decoration: none;
}
.action-btn:hover { transform: translateY(-2px); }
.btn-primary { background: linear-gradient(45deg, #b91c1c, #991b1b); color: white; }
.btn-secondary { background-color: #e5e7eb; color: #374151; }
.btn-danger { background-color: #dc2626; color: white; }
.action-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

/* --- Modal --- */
.modal-overlay { position: fixed; inset: 0; background-color: rgba(10, 20, 30, 0.6); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
.modal-content {
  background-color: white; border-radius: 15px; padding: 2.5rem;
  max-width: 500px; width: 90%; box-shadow: 0 20px 40px rgba(0,0,0,0.3);
  text-align: center;
}
.modal-icon {
  width: 3.5rem; height: 3.5rem; border-radius: 50%;
  background-color: #fee2e2; color: #dc2626;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 1.5rem auto; font-size: 1.5rem;
}
.modal-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; }
.modal-text { color: #4b5563; margin-bottom: 2rem; }
.modal-actions { display: flex; justify-content: center; gap: 1rem; }

/* --- Animaciones --- */
.animated-item { opacity: 0; animation: fadeInUp 0.7s ease-out forwards; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.spinner { width: 1.25rem; height: 1.25rem; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* --- Responsividad --- */
@media (max-width: 640px) {
  .page-header { flex-direction: column; align-items: flex-start; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>