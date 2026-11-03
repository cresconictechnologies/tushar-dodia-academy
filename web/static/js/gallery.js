// Photo Gallery & Lightbox Viewer for 100-Photo Archive

let allPhotos = [];
let currentCategory = 'all';
let currentPhotoIndex = 0;
let filteredPhotos = [];

async function initGallery() {
  const galleryGrid = document.getElementById('galleryGrid');
  if (!galleryGrid) return;

  try {
    const res = await fetch('/api/photos');
    allPhotos = await res.json();
    filteredPhotos = [...allPhotos];
    renderGallery();
    setupFilters();
    setupLightbox();
  } catch (err) {
    console.error('Failed to load photos:', err);
    galleryGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">Unable to load photographic archive. Please refresh.</div>';
  }
}

function setupFilters() {
  const pills = document.querySelectorAll('.filter-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentCategory = pill.getAttribute('data-category');
      
      if (currentCategory === 'all') {
        filteredPhotos = [...allPhotos];
      } else {
        filteredPhotos = allPhotos.filter(p => p.category_id === currentCategory);
      }
      renderGallery();
    });
  });
}

function renderGallery() {
  const galleryGrid = document.getElementById('galleryGrid');
  if (!galleryGrid) return;

  if (filteredPhotos.length === 0) {
    galleryGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">No photographs found in this category.</div>';
    return;
  }

  galleryGrid.innerHTML = filteredPhotos.map((photo, index) => `
    <div class="gallery-item" data-index="${index}">
      <img src="/dossier/${photo.relative_path}" alt="${escapeHtml(photo.title)}" loading="lazy">
      <div class="gallery-overlay">
        <div class="gallery-overlay-cat">${escapeHtml(photo.category_name)}</div>
        <div class="gallery-overlay-title">Page ${photo.page}: ${escapeHtml(photo.title)}</div>
      </div>
    </div>
  `).join('');

  // Bind click events to open lightbox
  document.querySelectorAll('.gallery-item').forEach(item => {
    item.addEventListener('click', () => {
      const idx = parseInt(item.getAttribute('data-index'), 10);
      openLightbox(idx);
    });
  });
}

function setupLightbox() {
  const modal = document.getElementById('lightboxModal');
  const closeBtn = document.getElementById('lightboxClose');
  const prevBtn = document.getElementById('lightboxPrev');
  const nextBtn = document.getElementById('lightboxNext');

  if (!modal) return;

  closeBtn?.addEventListener('click', closeLightbox);
  prevBtn?.addEventListener('click', showPrevPhoto);
  nextBtn?.addEventListener('click', showNextPhoto);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeLightbox();
  });

  document.addEventListener('keydown', (e) => {
    if (!modal.classList.contains('active')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') showPrevPhoto();
    if (e.key === 'ArrowRight') showNextPhoto();
  });
}

function openLightbox(index) {
  currentPhotoIndex = index;
  updateLightboxContent();
  const modal = document.getElementById('lightboxModal');
  if (modal) modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeLightbox() {
  const modal = document.getElementById('lightboxModal');
  if (modal) modal.classList.remove('active');
  document.body.style.overflow = '';
}

function showPrevPhoto() {
  if (filteredPhotos.length === 0) return;
  currentPhotoIndex = (currentPhotoIndex - 1 + filteredPhotos.length) % filteredPhotos.length;
  updateLightboxContent();
}

function showNextPhoto() {
  if (filteredPhotos.length === 0) return;
  currentPhotoIndex = (currentPhotoIndex + 1) % filteredPhotos.length;
  updateLightboxContent();
}

function updateLightboxContent() {
  const photo = filteredPhotos[currentPhotoIndex];
  if (!photo) return;

  const img = document.getElementById('lightboxImg');
  const title = document.getElementById('lightboxTitle');
  const desc = document.getElementById('lightboxDesc');
  const pageTag = document.getElementById('lightboxPage');

  if (img) img.src = `/dossier/${photo.relative_path}`;
  if (title) title.textContent = photo.title || `Slide / Page ${photo.page}`;
  if (desc) desc.textContent = photo.full_caption || '';
  if (pageTag) pageTag.textContent = `Slide ${photo.page} of 100 · ${photo.category_name}`;
}

function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

document.addEventListener('DOMContentLoaded', initGallery);
