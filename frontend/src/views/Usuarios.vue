<template>
  <div class="usuarios-page">
    <div class="header-section">
      <div>
        <h1 class="page-title">Usuarios</h1>
        <p class="page-subtitle">Gestiona los usuarios de tu sistema</p>
      </div>
      <button class="btn-primary" @click="openCreateModal">
        <span class="btn-icon">+</span>
        Nuevo Usuario
      </button>
    </div>

    <!-- Tabla de usuarios -->
    <div class="table-container">
      <table class="usuarios-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" class="table-row">
            <td>
              <span class="id-badge">#{{ user.id }}</span>
            </td>
            <td>
              <div class="user-cell">
                <div class="user-avatar">{{ user.name.charAt(0) }}</div>
                <span class="user-name">{{ user.name }}</span>
              </div>
            </td>
            <td>
              <span class="email-text">{{ user.email }}</span>
            </td>
            <td>
              <span :class="['role-badge', `role-${user.role}`]">
                {{ user.role === 'admin' ? 'Admin' : 'Usuario' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button @click="editUser(user)" class="btn-edit" title="Editar">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="deleteUser(user.id)" class="btn-delete" title="Eliminar">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Crear/Editar Usuario -->
    <transition name="modal">
      <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ editingUser ? 'Editar Usuario' : 'Nuevo Usuario' }}</h2>
            <button @click="closeModal" class="btn-close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="saveUser">
            <div class="form-group">
              <label>Nombre</label>
              <input type="text" v-model="form.name" required placeholder="Ingresa el nombre completo" />
            </div>
            
            <div class="form-group">
              <label>Email</label>
              <input type="email" v-model="form.email" required placeholder="correo@ejemplo.com" />
            </div>
            
            <div class="form-group">
              <label>Rol</label>
              <select v-model="form.role">
                <option value="admin">Admin</option>
                <option value="user">Usuario</option>
              </select>
            </div>
            
            <div class="modal-actions">
              <button type="button" @click="closeModal" class="btn-secondary">Cancelar</button>
              <button type="submit" class="btn-primary">
                {{ editingUser ? 'Actualizar' : 'Crear' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>

  </div>
</template>

<script>
export default {
  name: 'Usuarios',
  data() {
    return {
      users: [
        { id: 1, name: 'Juan Pérez', email: 'juan@example.com', role: 'admin' },
        { id: 2, name: 'Ana Gómez', email: 'ana@example.com', role: 'user' }
      ],
      showModal: false,
      editingUser: null,
      form: { id: null, name: '', email: '', role: 'user' }
    }
  },
  methods: {
    openCreateModal() {
      this.editingUser = null
      this.form = { id: null, name: '', email: '', role: 'user' }
      this.showModal = true
    },
    editUser(user) {
      this.editingUser = user
      this.form = { ...user }
      this.showModal = true
    },
    deleteUser(id) {
      if (confirm('¿Estás seguro de eliminar este usuario?')) {
        this.users = this.users.filter(u => u.id !== id)
      }
    },
    saveUser() {
      if (this.editingUser) {
        // Editar
        const index = this.users.findIndex(u => u.id === this.editingUser.id)
        if (index !== -1) this.users[index] = { ...this.form }
      } else {
        // Crear
        const newId = this.users.length
          ? Math.max(...this.users.map(u => u.id)) + 1
          : 1
        this.users.push({ ...this.form, id: newId })
      }
      this.closeModal()
    },
    closeModal() {
      this.showModal = false
    }
  }
}
</script>

<style scoped>
.usuarios-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.6);
  margin: 0.5rem 0 0 0;
  font-size: 0.95rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.btn-icon {
  font-size: 1.2rem;
  font-weight: 600;
}

.table-container {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
}

.usuarios-table {
  width: 100%;
  border-collapse: collapse;
}

.usuarios-table th {
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem 1.5rem;
  text-align: left;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.usuarios-table td {
  padding: 1.25rem 1.5rem;
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.table-row {
  transition: all 0.2s ease;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.id-badge {
  display: inline-block;
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1rem;
  flex-shrink: 0;
}

.user-name {
  font-weight: 500;
}

.email-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.role-badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.role-admin {
  background: rgba(234, 102, 102, 0.2);
  color: #ea6666;
  border: 1px solid rgba(234, 102, 102, 0.3);
}

.role-user {
  background: rgba(102, 234, 162, 0.2);
  color: #66eaa2;
  border: 1px solid rgba(102, 234, 162, 0.3);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-edit,
.btn-delete {
  border: none;
  background: rgba(255, 255, 255, 0.08);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-edit {
  color: #667eea;
}

.btn-edit:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
}

.btn-delete {
  color: #ea6666;
}

.btn-delete:hover {
  background: rgba(234, 102, 102, 0.2);
  transform: scale(1.1);
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  backdrop-filter: blur(5px);
}

.modal {
  background: linear-gradient(145deg, rgba(30, 30, 45, 0.98), rgba(20, 20, 35, 0.98));
  padding: 0;
  border-radius: 20px;
  min-width: 450px;
  max-width: 500px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
  margin: 0;
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
}

.btn-close {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.modal form {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.9rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  color: white;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 2rem;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.12);
}

/* Animaciones del modal */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .modal,
.modal-leave-active .modal {
  transition: transform 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal,
.modal-leave-to .modal {
  transform: scale(0.9);
}
</style>