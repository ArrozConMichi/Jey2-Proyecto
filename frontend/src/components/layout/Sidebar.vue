<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h3 class="sidebar-title">Menú Principal</h3>
      <div class="title-decoration"></div>
    </div>
    
    <nav class="sidebar-nav">
      <ul>
        <li v-for="link in links" :key="link.name">
          <router-link :to="link.path" class="nav-link" active-class="active">
            <div class="link-icon">
              <svg v-if="link.name === 'Inicio'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              <svg v-else-if="link.name === 'Usuarios'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              <svg v-else-if="link.name === 'Productos'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <path d="M16 10a4 4 0 0 1-8 0"></path>
              </svg>
              <svg v-else-if="link.name === 'Proveedores'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              <svg v-else-if="link.name === 'Ventas'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
              <svg v-else-if="link.name === 'Configuración'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6"></path>
                <path d="M12 1v6m0 6v6"></path>
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"></path>
              </svg>
            </div>
            <span class="link-text">{{ link.name }}</span>
            <div class="link-indicator"></div>
          </router-link>
        </li>
      </ul>
    </nav>
    
    <div class="sidebar-footer">
      <div class="version-info">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M12 16v-4"></path>
          <path d="M12 8h.01"></path>
        </svg>
        <span>Versión 1.0.0</span>
      </div>
    </div>
  </aside>
</template>

<script>
export default {
  name: "Sidebar",
  data() {
    return {
      links: [
        { name: "Inicio", path: "/", icon: "bx bx-home-alt" },
        { name: "Usuarios", path: "/usuarios", icon: "bx bx-user" },
        { name: "Productos", path: "/productos", icon: "bx bx-package" },
        { name: "Proveedores", path: "/proveedores", icon: "bx bx-store-alt" },
        { name: "Ventas", path: "/ventas", icon: "bx bx-cart" },
        { name: "Configuración", path: "/config", icon: "bx bx-cog" },
      ],
    };
  },
};
</script>

<style scoped>
.sidebar {
  width: 260px;
  min-height: 100vh;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.02) 100%
  );
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  transition: all 0.3s ease;
  position: relative;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(102, 126, 234, 0.3) 50%,
    transparent 100%
  );
}

.sidebar-header {
  margin-bottom: 2rem;
  padding: 0 0.5rem;
}

.sidebar-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 0.5rem 0;
}

.title-decoration {
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
}

.sidebar-nav {
  flex: 1;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
  overflow: hidden;
  text-decoration: none;
}

.nav-link::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 0;
  height: 100%;
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.15) 0%, transparent 100%);
  transition: width 0.3s ease;
  z-index: 0;
}

.nav-link:hover::before {
  width: 100%;
}

.nav-link:hover {
  color: #fff;
  transform: translateX(4px);
  background: rgba(255, 255, 255, 0.05);
}

.link-icon {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.nav-link:hover .link-icon {
  background: rgba(102, 126, 234, 0.15);
  transform: rotate(-5deg);
}

.link-icon svg {
  transition: all 0.3s ease;
}

.link-text {
  position: relative;
  z-index: 1;
  font-size: 0.95rem;
  font-weight: 500;
  flex: 1;
}

.link-indicator {
  position: absolute;
  right: 1rem;
  width: 0;
  height: 20px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
  z-index: 1;
}

.active {
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.2) 0%,
    rgba(118, 75, 162, 0.15) 100%
  );
  color: #fff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.active::before {
  width: 100%;
}

.active .link-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
}

.active .link-icon svg {
  filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.5));
}

.active .link-indicator {
  width: 4px;
}

.sidebar-footer {
  margin-top: auto;
  padding: 1rem 0.5rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.version-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}

.version-info svg {
  color: rgba(102, 126, 234, 0.6);
}

/* Responsive */
@media (max-width: 1024px) {
  .sidebar {
    width: 220px;
    padding: 1.25rem 0.75rem;
  }
  
  .nav-link {
    padding: 0.75rem 0.85rem;
  }
  
  .link-text {
    font-size: 0.9rem;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 70px;
    padding: 1.25rem 0.5rem;
  }
  
  .sidebar-title,
  .link-text,
  .version-info span {
    display: none;
  }
  
  .title-decoration {
    display: none;
  }
  
  .nav-link {
    justify-content: center;
    padding: 0.75rem;
  }
  
  .link-icon {
    margin: 0;
  }
  
  .version-info {
    justify-content: center;
  }
  
  .link-indicator {
    display: none;
  }
}
</style>