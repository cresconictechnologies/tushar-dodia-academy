// Main Frontend Interactions & Motion Logic

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Nav Toggle
  const toggleBtn = document.querySelector('.mobile-menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  
  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener('click', () => {
      const isVisible = navLinks.style.display === 'flex';
      navLinks.style.display = isVisible ? 'none' : 'flex';
      if (!isVisible) {
        navLinks.style.flexDirection = 'column';
        navLinks.style.position = 'absolute';
        navLinks.style.top = '72px';
        navLinks.style.left = '0';
        navLinks.style.right = '0';
        navLinks.style.background = '#ffffff';
        navLinks.style.padding = '24px';
        navLinks.style.boxShadow = '0 12px 30px rgba(0,0,0,0.1)';
        navLinks.style.borderBottom = '2px solid #e2e8f0';
      }
    });
  }

  // Animate Metric Counters
  const countElements = document.querySelectorAll('.counter-val');
  if ('IntersectionObserver' in window && countElements.length > 0) {
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const target = entry.target;
          const endValue = parseInt(target.getAttribute('data-target') || '0', 10);
          const duration = 1800;
          const startTime = performance.now();
          
          const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 3); // Ease out cubic
            const currentCount = Math.floor(easeProgress * endValue);
            target.textContent = currentCount.toLocaleString();
            
            if (progress < 1) {
              requestAnimationFrame(updateCounter);
            } else {
              target.textContent = endValue.toLocaleString() + (target.getAttribute('data-suffix') || '');
            }
          };
          
          requestAnimationFrame(updateCounter);
          obs.unobserve(target);
        }
      });
    }, { threshold: 0.2 });

    countElements.forEach(el => observer.observe(el));
  }

  // Register GSAP animations if available
  if (typeof gsap !== 'undefined') {
    // Hero timeline - only execute if hero elements exist on current page
    if (document.querySelector('.hero-title')) {
      if (document.querySelector('.hero-pill-tag')) gsap.from('.hero-pill-tag', { opacity: 0, y: -20, duration: 0.8, delay: 0.2, ease: 'power3.out' });
      gsap.from('.hero-title', { opacity: 0, y: 30, duration: 1, delay: 0.3, ease: 'power3.out' });
      if (document.querySelector('.hero-desc')) gsap.from('.hero-desc', { opacity: 0, y: 20, duration: 0.9, delay: 0.5, ease: 'power3.out' });
      if (document.querySelector('.hero-btn-group')) gsap.from('.hero-btn-group', { opacity: 0, y: 20, duration: 0.8, delay: 0.7, ease: 'power3.out' });
      if (document.querySelector('.hero-image-wrapper')) gsap.from('.hero-image-wrapper', { opacity: 0, scale: 0.95, duration: 1.1, delay: 0.4, ease: 'power3.out' });
      if (document.querySelector('.hero-floating-badge')) gsap.from('.hero-floating-badge', { opacity: 0, x: -30, duration: 0.9, delay: 0.9, ease: 'back.out(1.7)' });
    }

    // ScrollTrigger Card Staggers
    if (typeof ScrollTrigger !== 'undefined') {
      gsap.registerPlugin(ScrollTrigger);

      gsap.utils.toArray('.pillar-card').forEach((card, i) => {
        gsap.from(card, {
          scrollTrigger: {
            trigger: card,
            start: 'top 85%'
          },
          opacity: 0,
          y: 40,
          duration: 0.7,
          delay: i * 0.15,
          ease: 'power2.out'
        });
      });

      gsap.utils.toArray('.service-card').forEach((card, i) => {
        gsap.from(card, {
          scrollTrigger: {
            trigger: card,
            start: 'top 85%'
          },
          opacity: 0,
          y: 40,
          duration: 0.7,
          delay: (i % 3) * 0.12,
          ease: 'power2.out'
        });
      });
    }
  }
});
