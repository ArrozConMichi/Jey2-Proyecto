<template>
  <header class="navbar">
    <div class="logo">
      <div class="logo-container">
        <img src="/logo.png" alt="Logo" />
      </div>
      <h1 class="logo-text">Jey<span>2</span></h1>
    </div>
    
    <nav class="nav-actions">
      <button class="icon-btn" title="Notificaciones" @click="handleNotifications">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
        <span class="notification-badge">3</span>
      </button>
      
      <button class="icon-btn" title="Configuración" @click="handleSettings">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M12 1v6m0 6v6m5.2-13.2L15 8m-6 6l-2.2 2.2m10.4 0L15 14m-6-6L6.8 5.8"></path>
          <path d="M12 1v6m0 6v6"></path>
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"></path>
        </svg>
      </button>
      
      <div class="divider"></div>
      
      <div class="profile" title="Perfil" @click="handleProfile">
        <img src="https://i.pravatar.cc/40" alt="user avatar" />
        <div class="profile-status"></div>
      </div>
    </nav>
  </header>
</template>

<script>
export default {
  name: "Navbar",
  methods: {
    handleNotifications() {
      console.log('Notificaciones clicked');
    },
    handleSettings() {
      console.log('Configuración clicked');
    },
    handleProfile() {
      console.log('Perfil clicked');
    }
  }
};
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  backdrop-filter: blur(20px);
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.08) 0%,
    rgba(255, 255, 255, 0.03) 100%
  );
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: translateY(-2px);
}

.logo-container {
  position: relative;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.logo:hover .logo-container {
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
  transform: rotate(-5deg);
}

.logo-container img {
  width: 28px;
  height: 28px;
  object-fit: contain;
  filter: brightness(0) invert(1);
}

.logo-text {
  font-weight: 700;
  font-size: 1.5rem;
  color: #fff;
  margin: 0;
  letter-spacing: -0.5px;
}

.logo-text span {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon-btn {
  position: relative;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.icon-btn:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
  color: #667eea;
  transform: translateY(-2px);
}

.icon-btn:active {
  transform: translateY(0);
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: linear-gradient(135deg, #ea6666 0%, #c94545 100%);
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.35rem;
  border-radius: 10px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(234, 102, 102, 0.4);
  animation: pulse-badge 2s ease-in-out infinite;
}

@keyframes pulse-badge {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0 0.5rem;
}

.profile {
  position: relative;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.profile:hover {
  transform: scale(1.05);
}

.profile img {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: 2px solid transparent;
  background: linear-gradient(white, white) padding-box,
              linear-gradient(135deg, #667eea 0%, #764ba2 100%) border-box;
  object-fit: cover;
  transition: all 0.3s ease;
}

.profile:hover img {
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.profile-status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: #66eaa2;
  border: 2px solid rgba(20, 20, 35, 1);
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(102, 234, 162, 0.6);
}

/* Responsive */
@media (max-width: 768px) {
  .navbar {
    padding: 1rem 1.5rem;
  }
  
  .logo-text {
    font-size: 1.3rem;
  }
  
  .divider {
    display: none;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 0.75rem 1rem;
  }
  
  .logo-container {
    width: 38px;
    height: 38px;
  }
  
  .logo-container img {
    width: 24px;
    height: 24px;
  }
  
  .icon-btn {
    width: 38px;
    height: 38px;
  }
  
  .profile img {
    width: 38px;
    height: 38px;
  }
}
</style>