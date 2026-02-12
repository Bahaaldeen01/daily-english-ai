/* ══════════════════════════════════════
   Daily Phrase – App Logic
   ══════════════════════════════════════ */

(function () {
  'use strict';

  // ─── Theme Toggle ───
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);

    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateThemeIcon(next);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    themeToggle.innerHTML = theme === 'dark' ? '☀️ فاتح' : '🌙 داكن';
  }

  // ─── Progress Tracking ───
  function getVisitedLessons() {
    return JSON.parse(localStorage.getItem('visitedLessons') || '[]');
  }

  function markLessonVisited(dateStr) {
    const visited = getVisitedLessons();
    if (!visited.includes(dateStr)) {
      visited.push(dateStr);
      localStorage.setItem('visitedLessons', JSON.stringify(visited));
    }
  }

  // Update progress bar on index page
  const progressFill = document.getElementById('progressFill');
  const progressCount = document.getElementById('progressCount');
  if (progressFill && progressCount) {
    const totalLessons = document.querySelectorAll('.lesson-item').length;
    const visited = getVisitedLessons();
    const visitedCount = document.querySelectorAll('.lesson-item').length > 0
      ? [...document.querySelectorAll('.lesson-item')]
          .filter(item => visited.includes(item.dataset.date)).length
      : 0;

    const percent = totalLessons > 0 ? (visitedCount / totalLessons) * 100 : 0;
    progressFill.style.width = percent + '%';
    progressCount.textContent = `${visitedCount} / ${totalLessons}`;

    // Mark visited items
    document.querySelectorAll('.lesson-item').forEach(item => {
      if (visited.includes(item.dataset.date)) {
        item.classList.add('visited');
      }
    });

    // Streak calculation
    const streakEl = document.getElementById('streakCount');
    if (streakEl) {
      const streak = calculateStreak(visited);
      streakEl.textContent = streak;
    }
  }

  function calculateStreak(visited) {
    if (visited.length === 0) return 0;
    const sorted = [...visited].sort().reverse();
    const today = new Date().toISOString().split('T')[0];
    let streak = 0;
    let checkDate = new Date(today);

    for (let i = 0; i < 365; i++) {
      const dateStr = checkDate.toISOString().split('T')[0];
      if (sorted.includes(dateStr)) {
        streak++;
        checkDate.setDate(checkDate.getDate() - 1);
      } else {
        break;
      }
    }
    return streak;
  }

  // Mark current lesson as visited
  const lessonDateEl = document.getElementById('lessonDate');
  if (lessonDateEl) {
    markLessonVisited(lessonDateEl.dataset.date);
  }

  // ─── Search Functionality ───
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      document.querySelectorAll('.lesson-item').forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? '' : 'none';
      });
    });
  }

  // ─── Sound Buttons ───
  document.querySelectorAll('[data-audio]').forEach(btn => {
    btn.addEventListener('click', () => {
      const src = btn.dataset.audio;
      const audio = new Audio(src);
      btn.classList.add('playing');
      audio.play();
      audio.addEventListener('ended', () => {
        btn.classList.remove('playing');
      });
    });
  });

  // ─── Quiz Logic ───
  const quizForms = document.querySelectorAll('.quiz-block');
  let totalQuestions = quizForms.length;
  let correctAnswers = 0;
  let answeredQuestions = 0;

  quizForms.forEach((block, idx) => {
    const options = block.querySelectorAll('.quiz-option');
    const correctIdx = parseInt(block.dataset.correct);
    const resultEl = block.querySelector('.quiz-result');

    options.forEach((opt, optIdx) => {
      opt.addEventListener('click', () => {
        if (opt.disabled) return;

        // Disable all options
        options.forEach(o => o.disabled = true);

        answeredQuestions++;

        if (optIdx === correctIdx) {
          opt.classList.add('correct');
          resultEl.textContent = '✅ إجابة صحيحة!';
          resultEl.className = 'quiz-result show success';
          correctAnswers++;
        } else {
          opt.classList.add('wrong');
          options[correctIdx].classList.add('correct');
          resultEl.textContent = '❌ إجابة خاطئة';
          resultEl.className = 'quiz-result show fail';
        }

        // Show final score
        if (answeredQuestions === totalQuestions) {
          const scoreEl = document.getElementById('quizScore');
          if (scoreEl) {
            scoreEl.textContent = `نتيجتك: ${correctAnswers} / ${totalQuestions}`;
            scoreEl.classList.add('show');
          }
        }
      });
    });
  });

  // ─── Share Buttons ───
  const shareUrl = window.location.href;
  const shareText = document.querySelector('.lesson-phrase')?.textContent || 'Daily Phrase';

  const waBtn = document.getElementById('shareWhatsapp');
  if (waBtn) {
    waBtn.href = `https://wa.me/?text=${encodeURIComponent(shareText + ' ' + shareUrl)}`;
  }

  const twBtn = document.getElementById('shareTwitter');
  if (twBtn) {
    twBtn.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`;
  }

  const tgBtn = document.getElementById('shareTelegram');
  if (tgBtn) {
    tgBtn.href = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`;
  }

  const copyBtn = document.getElementById('shareCopy');
  if (copyBtn) {
    copyBtn.addEventListener('click', (e) => {
      e.preventDefault();
      navigator.clipboard.writeText(shareUrl).then(() => {
        copyBtn.textContent = '✅ تم النسخ!';
        setTimeout(() => {
          copyBtn.innerHTML = '🔗 نسخ الرابط';
        }, 2000);
      });
    });
  }

  // ─── PWA Install Prompt ───
  let deferredPrompt;
  const installBanner = document.getElementById('installBanner');

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBanner) installBanner.classList.add('show');
  });

  if (installBanner) {
    installBanner.addEventListener('click', () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(() => {
          deferredPrompt = null;
          installBanner.classList.remove('show');
        });
      }
    });
  }

  // ─── Service Worker Registration ───
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  }

})();
