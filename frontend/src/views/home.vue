<template>
  <div class="home-page">
    <!-- Header Section -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="dashboard-title">
            <span class="icon-wrapper">🏠</span>
            Dashboard
          </h1>
          <p class="dashboard-subtitle">Bienvenido de nuevo • {{ currentDate }}</p>
        </div>
        <div class="quick-actions">
          <button class="action-btn primary">
            <span class="btn-icon">📊</span>
            Ver Reportes
          </button>
          <button class="action-btn secondary">
            <span class="btn-icon">⚙️</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Cards Grid -->
    <div class="stats-grid">
      <div class="stat-card usuarios-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <div class="stat-header">
            <div class="stat-icon usuarios">👥</div>
            <span class="stat-trend positive">+12.5%</span>
          </div>
          <div class="stat-value">{{ animatedUsers }}</div>
          <div class="stat-label">Usuarios Activos</div>
          <div class="stat-footer">
            <div class="mini-chart">
              <div class="chart-bar" style="height: 40%"></div>
              <div class="chart-bar" style="height: 65%"></div>
              <div class="chart-bar" style="height: 45%"></div>
              <div class="chart-bar" style="height: 80%"></div>
              <div class="chart-bar" style="height: 100%"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="stat-card productos-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <div class="stat-header">
            <div class="stat-icon productos">📦</div>
            <span class="stat-trend positive">+8.3%</span>
          </div>
          <div class="stat-value">{{ animatedProducts }}</div>
          <div class="stat-label">Productos en Stock</div>
          <div class="stat-footer">
            <div class="mini-chart">
              <div class="chart-bar" style="height: 60%"></div>
              <div class="chart-bar" style="height: 75%"></div>
              <div class="chart-bar" style="height: 55%"></div>
              <div class="chart-bar" style="height: 90%"></div>
              <div class="chart-bar" style="height: 85%"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="stat-card ventas-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <div class="stat-header">
            <div class="stat-icon ventas">💰</div>
            <span class="stat-trend positive">+24.7%</span>
          </div>
          <div class="stat-value">$ {{ animatedSales.toLocaleString() }}</div>
          <div class="stat-label">Ventas del Mes</div>
          <div class="stat-footer">
            <div class="mini-chart">
              <div class="chart-bar" style="height: 50%"></div>
              <div class="chart-bar" style="height: 70%"></div>
              <div class="chart-bar" style="height: 85%"></div>
              <div class="chart-bar" style="height: 95%"></div>
              <div class="chart-bar" style="height: 100%"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="stat-card ingresos-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <div class="stat-header">
            <div class="stat-icon ingresos">📈</div>
            <span class="stat-trend positive">+18.2%</span>
          </div>
          <div class="stat-value">$ {{ animatedRevenue.toLocaleString() }}</div>
          <div class="stat-label">Ingresos Totales</div>
          <div class="stat-footer">
            <div class="mini-chart">
              <div class="chart-bar" style="height: 45%"></div>
              <div class="chart-bar" style="height: 60%"></div>
              <div class="chart-bar" style="height: 75%"></div>
              <div class="chart-bar" style="height: 88%"></div>
              <div class="chart-bar" style="height: 95%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Coming Soon Section -->
    <div class="coming-soon-section">
      <div class="coming-soon-card">
        <div class="particles">
          <span class="particle">✨</span>
          <span class="particle">🚀</span>
          <span class="particle">💫</span>
          <span class="particle">⭐</span>
        </div>
        <div class="coming-soon-content">
          <h2 class="coming-soon-title">Próximamente</h2>
          <p class="coming-soon-text">
            Gráficos avanzados, análisis en tiempo real y reportes detallados
          </p>
          <div class="feature-list">
            <div class="feature-item">Gráficos Interactivos</div>
            <div class="feature-item">Métricas en Tiempo Real</div>
            <div class="feature-item">Análisis Predictivo</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      animatedUsers: 0,
      animatedProducts: 0,
      animatedSales: 0,
      animatedRevenue: 0,
      targetUsers: 1247,
      targetProducts: 856,
      targetSales: 45680,
      targetRevenue: 128450
    }
  },
  computed: {
    currentDate() {
      const options = { year: 'numeric', month: 'long', day: 'numeric' }
      return new Date().toLocaleDateString('es-ES', options)
    }
  },
  mounted() {
    this.animateValues()
  },
  methods: {
    animateValues() {
      const duration = 2000
      const steps = 60
      const interval = duration / steps

      const animate = (start, end, key) => {
        let current = start
        const increment = (end - start) / steps
        const timer = setInterval(() => {
          current += increment
          if (current >= end) {
            this[key] = end
            clearInterval(timer)
          } else {
            this[key] = Math.floor(current)
          }
        }, interval)
      }

      setTimeout(() => animate(0, this.targetUsers, 'animatedUsers'), 100)
      setTimeout(() => animate(0, this.targetProducts, 'animatedProducts'), 200)
      setTimeout(() => animate(0, this.targetSales, 'animatedSales'), 300)
      setTimeout(() => animate(0, this.targetRevenue, 'animatedRevenue'), 400)
    }
  }
}
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 1rem;
}

/* Dashboard Header */
.dashboard-header {
  animation: slideDown 0.6s ease-out;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.title-section {
  flex: 1;
}

.dashboard-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 1rem;
  animation: fadeIn 0.8s ease-out;
}

.icon-wrapper {
  display: inline-block;
  animation: bounce 2s infinite;
}

.dashboard-subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.95rem;
  margin: 0.5rem 0 0 0;
  font-weight: 400;
}

.quick-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
  padding: 0.75rem 1rem;
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.btn-icon {
  font-size: 1.1rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
  animation: fadeInUp 0.8s ease-out 0.2s both;
}

.stat-card {
  position: relative;
  padding: 1.75rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-8px);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
}

.stat-card:hover::before {
  opacity: 1;
}

.card-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200px;
  height: 200px;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.5s ease;
  filter: blur(40px);
  pointer-events: none;
}

.stat-card:hover .card-glow {
  opacity: 0.3;
}

.usuarios-card .card-glow {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.productos-card .card-glow {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.ventas-card .card-glow {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.ingresos-card .card-glow {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.card-content {
  position: relative;
  z-index: 1;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  transition: transform 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.1) rotate(5deg);
}

.stat-icon.usuarios {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
}

.stat-icon.productos {
  background: linear-gradient(135deg, rgba(240, 147, 251, 0.2) 0%, rgba(245, 87, 108, 0.2) 100%);
}

.stat-icon.ventas {
  background: linear-gradient(135deg, rgba(79, 172, 254, 0.2) 0%, rgba(0, 242, 254, 0.2) 100%);
}

.stat-icon.ingresos {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.2) 0%, rgba(56, 249, 215, 0.2) 100%);
}

.stat-trend {
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  backdrop-filter: blur(10px);
}

.stat-trend.positive {
  background: rgba(67, 233, 123, 0.2);
  color: #43e97b;
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 800;
  color: white;
  margin-bottom: 0.5rem;
  animation: countUp 1s ease-out;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.stat-footer {
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  gap: 0.4rem;
  height: 40px;
}

.chart-bar {
  flex: 1;
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.4) 100%);
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
  animation: growUp 0.8s ease-out both;
}

.productos-card .chart-bar {
  background: linear-gradient(180deg, rgba(240, 147, 251, 0.8) 0%, rgba(245, 87, 108, 0.4) 100%);
}

.ventas-card .chart-bar {
  background: linear-gradient(180deg, rgba(79, 172, 254, 0.8) 0%, rgba(0, 242, 254, 0.4) 100%);
}

.ingresos-card .chart-bar {
  background: linear-gradient(180deg, rgba(67, 233, 123, 0.8) 0%, rgba(56, 249, 215, 0.4) 100%);
}

.stat-card:hover .chart-bar {
  transform: scaleY(1.1);
}

.chart-bar:nth-child(1) { animation-delay: 0.1s; }
.chart-bar:nth-child(2) { animation-delay: 0.2s; }
.chart-bar:nth-child(3) { animation-delay: 0.3s; }
.chart-bar:nth-child(4) { animation-delay: 0.4s; }
.chart-bar:nth-child(5) { animation-delay: 0.5s; }

/* Coming Soon Section */
.coming-soon-section {
  animation: fadeInUp 0.8s ease-out 0.4s both;
}

.coming-soon-card {
  position: relative;
  padding: 3rem;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  text-align: center;
}

.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.particle {
  position: absolute;
  font-size: 2rem;
  animation: float-particle 6s infinite ease-in-out;
  opacity: 0.3;
}

.particle:nth-child(1) {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.particle:nth-child(2) {
  top: 60%;
  right: 15%;
  animation-delay: -2s;
}

.particle:nth-child(3) {
  bottom: 30%;
  left: 20%;
  animation-delay: -4s;
}

.particle:nth-child(4) {
  top: 40%;
  right: 25%;
  animation-delay: -1s;
}

.coming-soon-content {
  position: relative;
  z-index: 1;
}

.coming-soon-title {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
}

.coming-soon-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  margin-bottom: 2rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.feature-list {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.feature-item {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

/* Animations */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes growUp {
  from {
    transform: scaleY(0);
  }
  to {
    transform: scaleY(1);
  }
}

@keyframes countUp {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes float-particle {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -30px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(240deg);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-title {
    font-size: 2rem;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .coming-soon-card {
    padding: 2rem 1.5rem;
  }

  .feature-list {
    flex-direction: column;
    gap: 0.75rem;
  }

  .quick-actions {
    width: 100%;
  }

  .action-btn {
    flex: 1;
  }
}
</style>