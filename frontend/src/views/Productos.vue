<template>
  <div class="productos-page">
    <div class="header-section">
      <div>
        <h1 class="page-title">Productos</h1>
        <p class="page-subtitle">Administra tu inventario de productos</p>
      </div>
      <button class="btn-primary" @click="openCreateModal">
        <span class="btn-icon">+</span>
        Nuevo Producto
      </button>
    </div>

    <!-- Tabla de productos -->
    <div class="table-container">
      <table class="product-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Producto</th>
            <th>Categoría</th>
            <th>Precio</th>
            <th>Stock</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="producto in productos" :key="producto.id" class="table-row">
            <td>
              <span class="id-badge">#{{ producto.id }}</span>
            </td>
            <td>
              <div class="product-cell">
                <div class="product-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <path d="M16 10a4 4 0 0 1-8 0"></path>
                  </svg>
                </div>
                <span class="product-name">{{ producto.nombre }}</span>
              </div>
            </td>
            <td>
              <span class="category-badge">{{ producto.categoria }}</span>
            </td>
            <td>
              <span class="price-text">${{ producto.precio.toFixed(2) }}</span>
            </td>
            <td>
              <span :class="['stock-badge', {'low-stock': producto.stock < 10}]">
                <svg v-if="producto.stock < 10" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                  <line x1="12" y1="9" x2="12" y2="13"></line>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                {{ producto.stock }} unidades
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button @click="editProducto(producto)" class="btn-edit" title="Editar">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="deleteProducto(producto.id)" class="btn-delete" title="Eliminar">
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

    <!-- Modal Crear/Editar Producto -->
    <transition name="modal">
      <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ editingProducto ? 'Editar Producto' : 'Nuevo Producto' }}</h2>
            <button @click="closeModal" class="btn-close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="saveProducto">
            <div class="form-group">
              <label>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                  <line x1="3" y1="6" x2="21" y2="6"></line>
                  <path d="M16 10a4 4 0 0 1-8 0"></path>
                </svg>
                Nombre del Producto
              </label>
              <input v-model="form.nombre" placeholder="Ej: Arroz integral" required />
            </div>
            
            <div class="form-group">
              <label>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="7" height="7"></rect>
                  <rect x="14" y="3" width="7" height="7"></rect>
                  <rect x="14" y="14" width="7" height="7"></rect>
                  <rect x="3" y="14" width="7" height="7"></rect>
                </svg>
                Categoría
              </label>
              <input v-model="form.categoria" placeholder="Ej: Granos" required />
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="12" y1="1" x2="12" y2="23"></line>
                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                  </svg>
                  Precio
                </label>
                <input v-model.number="form.precio" type="number" step="0.01" placeholder="0.00" required />
              </div>
              
              <div class="form-group">
                <label>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                  </svg>
                  Stock
                </label>
                <input v-model.number="form.stock" type="number" placeholder="0" required />
              </div>
            </div>
            
            <div class="modal-actions">
              <button type="button" @click="closeModal" class="btn-secondary">Cancelar</button>
              <button type="submit" class="btn-primary">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                  <polyline points="17 21 17 13 7 13 7 21"></polyline>
                  <polyline points="7 3 7 8 15 8"></polyline>
                </svg>
                {{ editingProducto ? 'Actualizar' : 'Guardar' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref } from 'vue'

const productos = ref([
  { id: 1, nombre: 'Arroz', categoria: 'Granos', precio: 2.5, stock: 20 },
  { id: 2, nombre: 'Azúcar', categoria: 'Granos', precio: 1.8, stock: 8 },
  { id: 3, nombre: 'Aceite', categoria: 'Aceites', precio: 4.5, stock: 12 },
])

const showModal = ref(false)
const editingProducto = ref(null)
const form = ref({ nombre: '', categoria: '', precio: 0, stock: 0 })

function openCreateModal() {
  editingProducto.value = null
  form.value = { nombre: '', categoria: '', precio: 0, stock: 0 }
  showModal.value = true
}

function editProducto(producto) {
  editingProducto.value = producto
  form.value = { ...producto }
  showModal.value = true
}

function saveProducto() {
  if (editingProducto.value) {
    const index = productos.value.findIndex(p => p.id === editingProducto.value.id)
    productos.value[index] = { ...form.value }
  } else {
    const newId = productos.value.length ? Math.max(...productos.value.map(p => p.id)) + 1 : 1
    productos.value.push({ id: newId, ...form.value })
  }
  closeModal()
}

function deleteProducto(id) {
  if (confirm('¿Seguro que quieres eliminar este producto?')) {
    productos.value = productos.value.filter(p => p.id !== id)
  }
}

function closeModal() {
  showModal.value = false
}
</script>

<style scoped>
.productos-page {
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

.product-table {
  width: 100%;
  border-collapse: collapse;
}

.product-table th {
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

.product-table td {
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

.product-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.product-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.product-name {
  font-weight: 500;
}

.category-badge {
  display: inline-block;
  background: rgba(102, 234, 162, 0.15);
  color: #66eaa2;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid rgba(102, 234, 162, 0.3);
}

.price-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #66eaa2;
}

.stock-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  background: rgba(102, 234, 234, 0.15);
  color: #66eaea;
  border: 1px solid rgba(102, 234, 234, 0.3);
}

.stock-badge.low-stock {
  background: rgba(234, 102, 102, 0.2);
  color: #ea6666;
  border: 1px solid rgba(234, 102, 102, 0.3);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
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
  min-width: 500px;
  max-width: 550px;
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.9rem;
}

.form-group label svg {
  color: #667eea;
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
  box-sizing: border-box;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
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