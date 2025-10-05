<template>
  <div class="home-container">
    <!-- HEADER -->
    <header class="home-header">
      <h1 class="welcome-text">🚀 Bienvenido a <span class="brand">Jey2</span></h1>
      <p class="subtitle">Sistema de Gestión - Abarrotería, Carnicería y Bodega Elda</p>
    </header>

    <!-- STATS -->
    <section class="stats-section">
      <div
        v-for="stat in stats"
        :key="stat.id"
        class="stat-card"
        :style="{ backgroundColor: stat.color }"
      >
        <div class="stat-title">{{ stat.title }}</div>
        <div class="stat-value">{{ stat.value }}</div>
      </div>
    </section>

    <!-- ALERTS -->
    <section class="alerts-section" v-if="alerts.length">
      <h2 class="section-title">⚠️ Alertas del día</h2>
      <ul class="alert-list">
        <li
          v-for="alert in alerts"
          :key="alert.id"
          class="alert-item"
        >
          {{ alert.message }}
        </li>
      </ul>
    </section>

    <!-- QUICK ACCESS -->
    <section class="quick-access">
      <h2 class="section-title">Accesos rápidos</h2>
      <div class="access-buttons">
        <button v-for="btn in buttons" :key="btn.name" @click="goTo(btn.route)" class="btn-access">
          {{ btn.icon }} {{ btn.label }}
        </button>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "HomeViewPro",
  data() {
    return {
      stats: [
        { id: 1, title: "Ventas del día", value: "$520.00", color: "#f97316" },
        { id: 2, title: "Productos en stock", value: "324", color: "#22c55e" },
        { id: 3, title: "Proveedores activos", value: "12", color: "#3b82f6" },
        { id: 4, title: "Usuarios registrados", value: "8", color: "#f43f5e" },
      ],
      alerts: [
        { id: 1, message: "Producto 'Carne de res' con stock bajo (5 unidades)." },
        { id: 2, message: "Factura pendiente de pago con Proveedor XYZ." },
      ],
      buttons: [
        { name: "productos", label: "Productos", route: "productos", icon: "🛒" },
        { name: "ventas", label: "Ventas", route: "ventas", icon: "💰" },
        { name: "proveedores", label: "Proveedores", route: "proveedores", icon: "🚚" },
        { name: "usuarios", label: "Usuarios", route: "usuarios", icon: "👥" },
      ],
    };
  },
  methods: {
    goTo(route) {
      this.$router.push({ name: route });
    },
  },
};
</script>

<style scoped>
/* 🌟 CONTAINERS */
.home-container {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  font-family: 'Segoe UI', sans-serif;
}

/* HEADER */
.home-header {
  text-align: center;
}

.welcome-text {
  font-size: 2.25rem;
  font-weight: bold;
  animation: fadeIn 1s ease forwards;
}

.brand {
  color: #3b82f6;
}

.subtitle {
  color: #555;
  font-size: 1rem;
  margin-top: 0.25rem;
  animation: fadeIn 1.5s ease forwards;
}

/* STATS CARDS */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  border-radius: 12px;
  padding: 1.5rem;
  color: #fff;
  text-align: center;
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
  transform: translateY(20px);
  opacity: 0;
  animation: slideUp 0.8s forwards;
}

.stat-card:nth-child(1) { animation-delay: 0.2s; }
.stat-card:nth-child(2) { animation-delay: 0.4s; }
.stat-card:nth-child(3) { animation-delay: 0.6s; }
.stat-card:nth-child(4) { animation-delay: 0.8s; }

.stat-title {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: bold;
}

/* ALERTS */
.alerts-section {
  background: #fef3c7;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  animation: fadeIn 1s ease forwards;
}

.section-title {
  font-weight: bold;
  margin-bottom: 0.75rem;
}

.alert-list {
  list-style: disc;
  padding-left: 1.25rem;
}

.alert-item {
  margin-bottom: 0.5rem;
}

/* QUICK ACCESS BUTTONS */
.quick-access {
  text-align: center;
}

.access-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}

.btn-access {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.95rem;
  transition: transform 0.2s, background 0.3s;
}

.btn-access:hover {
  background-color: #1e40af;
  transform: translateY(-3px);
}

/* ANIMACIONES */
@keyframes slideUp {
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
