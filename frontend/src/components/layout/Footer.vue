<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-brand">
        <span class="brand-name">Jey<span class="brand-highlight">2</span></span>
        <span class="separator">|</span>
        <span class="tagline">Sistema de Gestión</span>
      </div>
      
      <div class="footer-info">
        <p class="copyright">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M15 9a3 3 0 0 0-6 0v6a3 3 0 0 0 6 0"></path>
          </svg>
          {{ new Date().getFullYear() }} Todos los derechos reservados
        </p>
        <span class="dot">•</span>
        <p class="made-with">
          Desarrollado con
          <span class="heart">💜</span>
          en
          <span class="os">Pop!_OS</span>
        </p>
      </div>
      
      <div class="footer-links">
        <a href="#" class="footer-link">Privacidad</a>
        <span class="dot">•</span>
        <a href="#" class="footer-link">Términos</a>
        <span class="dot">•</span>
        <a href="#" class="footer-link">Soporte</a>
      </div>
    </div>
    
    <div class="footer-decoration"></div>
  </footer>
</template>

<script>
export default {
  name: "Footer",
};
</script>

<style scoped>
.footer {
  position: relative;
  margin-top: auto;
  padding: 2rem 2rem 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.02) 100%
  );
  overflow: hidden;
}

.footer-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    #667eea 25%,
    #764ba2 50%,
    #667eea 75%,
    transparent 100%
  );
  opacity: 0.6;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.brand-name {
  font-weight: 700;
  color: white;
  letter-spacing: -0.3px;
}

.brand-highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
}

.separator {
  color: rgba(255, 255, 255, 0.3);
  font-weight: 300;
}

.tagline {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  font-weight: 400;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
  font-size: 0.85rem;
}

.copyright {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
}

.copyright svg {
  color: rgba(255, 255, 255, 0.4);
}

.made-with {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
}

.heart {
  display: inline-block;
  animation: heartbeat 1.5s ease-in-out infinite;
  font-size: 1rem;
}

@keyframes heartbeat {
  0%, 100% {
    transform: scale(1);
  }
  10%, 30% {
    transform: scale(1.2);
  }
  20%, 40% {
    transform: scale(1);
  }
}

.os {
  font-weight: 600;
  background: linear-gradient(135deg, #66eaa2 0%, #66eaea 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  padding: 0 0.2rem;
}

.dot {
  color: rgba(255, 255, 255, 0.3);
  font-weight: 300;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.footer-link {
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
}

.footer-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.footer-link:hover {
  color: #667eea;
}

.footer-link:hover::after {
  width: 100%;
}

/* Responsive */
@media (max-width: 768px) {
  .footer {
    padding: 1.5rem 1.5rem 1rem;
  }
  
  .footer-brand {
    font-size: 0.9rem;
  }
  
  .footer-info {
    font-size: 0.8rem;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .footer-info .dot {
    display: none;
  }
  
  .footer-links {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .footer {
    padding: 1.25rem 1rem 0.75rem;
  }
  
  .footer-content {
    gap: 0.75rem;
  }
  
  .footer-brand {
    flex-direction: column;
    gap: 0.25rem;
    text-align: center;
  }
  
  .footer-brand .separator {
    display: none;
  }
  
  .footer-links {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>