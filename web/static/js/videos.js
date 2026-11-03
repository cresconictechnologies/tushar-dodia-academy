// YouTube Video Vault & Player Modal

let allVideos = [];
let filteredVideos = [];
let activeVideoCategory = 'all';

async function initVideos() {
  const container = document.getElementById('videosGrid');
  if (!container) return;

  try {
    const res = await fetch('/api/videos');
    allVideos = await res.json();
    filteredVideos = [...allVideos];
    renderVideos();
    setupVideoFilters();
    setupVideoSearch();
    setupVideoModal();
  } catch (err) {
    console.error('Failed to load videos:', err);
    container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">Unable to load video vault. Please refresh.</div>';
  }
}

function setupVideoFilters() {
  const pills = document.querySelectorAll('.filter-pill[data-videocat]');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeVideoCategory = pill.getAttribute('data-videocat');
      applyVideoFilterAndSearch();
    });
  });
}

function setupVideoSearch() {
  const searchInput = document.getElementById('videoSearchInput');
  if (!searchInput) return;

  searchInput.addEventListener('input', () => {
    applyVideoFilterAndSearch();
  });
}

function applyVideoFilterAndSearch() {
  const searchInput = document.getElementById('videoSearchInput');
  const query = (searchInput ? searchInput.value : '').toLowerCase().trim();

  filteredVideos = allVideos.filter(v => {
    const titleMatch = v.title.toLowerCase().includes(query);
    if (!titleMatch) return false;

    if (activeVideoCategory === 'all') return true;
    if (activeVideoCategory === '2mins') {
      return v.title.toLowerCase().includes('2 min') || v.title.toLowerCase().includes('episode');
    }
    if (activeVideoCategory === 'student') {
      return v.title.toLowerCase().includes('student') || v.title.toLowerCase().includes('career') || v.title.toLowerCase().includes('study') || v.title.toLowerCase().includes('exam');
    }
    if (activeVideoCategory === 'finance') {
      return v.title.toLowerCase().includes('finance') || v.title.toLowerCase().includes('bank') || v.title.toLowerCase().includes('money') || v.title.toLowerCase().includes('cfa');
    }
    if (activeVideoCategory === 'parenting') {
      return v.title.toLowerCase().includes('parent') || v.title.toLowerCase().includes('संस्कार') || v.title.toLowerCase().includes('परिवार');
    }
    return true;
  });

  renderVideos();
}

function renderVideos() {
  const grid = document.getElementById('videosGrid');
  const countBadge = document.getElementById('videoCountBadge');
  if (!grid) return;

  if (countBadge) {
    countBadge.textContent = `Showing ${filteredVideos.length} of ${allVideos.length} Episodes`;
  }

  if (filteredVideos.length === 0) {
    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748b;">No videos found matching your query.</div>';
    return;
  }

  grid.innerHTML = filteredVideos.map(video => {
    const thumb = (video.thumbnails && video.thumbnails.length > 0) 
      ? video.thumbnails[video.thumbnails.length - 1].url 
      : `https://i.ytimg.com/vi/${video.id}/hqdefault.jpg`;
    
    const durationMin = video.duration ? Math.floor(video.duration / 60) : 2;
    const durationSec = video.duration ? (video.duration % 60).toString().padStart(2, '0') : '00';
    const durationStr = `${durationMin}:${durationSec}`;

    return `
      <div class="video-card">
        <div class="video-thumb-box" onclick="playVideoModal('${video.id}', '${escapeHtml(video.title)}')">
          <img src="${thumb}" alt="${escapeHtml(video.title)}" class="video-thumb-img" loading="lazy">
          <div class="video-play-btn"><i class="fa-solid fa-play"></i></div>
          <div class="video-duration-badge">${durationStr}</div>
        </div>
        <div class="video-card-body">
          <h3 class="video-title" title="${escapeHtml(video.title)}">${escapeHtml(video.title)}</h3>
          <div class="video-card-meta">
            <span><i class="fa-solid fa-eye" style="color:var(--saffron-dark);"></i> ${video.view_count ? video.view_count.toLocaleString() : '100+'} views</span>
            <a href="${video.url}" target="_blank" style="color:var(--text-secondary); font-size:0.75rem; font-weight:600;" onclick="event.stopPropagation()">
              <i class="fa-brands fa-youtube" style="color:#ef4444;"></i> Watch on YouTube
            </a>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function setupVideoModal() {
  const modal = document.getElementById('videoPlayerModal');
  const closeBtn = document.getElementById('videoPlayerClose');

  if (!modal) return;

  closeBtn?.addEventListener('click', closeVideoModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeVideoModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeVideoModal();
    }
  });
}

function playVideoModal(videoId, title) {
  const modal = document.getElementById('videoPlayerModal');
  const iframe = document.getElementById('videoIframe');
  const titleBox = document.getElementById('videoModalTitle');

  if (!modal || !iframe) return;

  iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
  if (titleBox) titleBox.textContent = title;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeVideoModal() {
  const modal = document.getElementById('videoPlayerModal');
  const iframe = document.getElementById('videoIframe');

  if (modal) modal.classList.remove('active');
  if (iframe) iframe.src = '';
  document.body.style.overflow = '';
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

document.addEventListener('DOMContentLoaded', initVideos);
