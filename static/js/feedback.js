/**
 * Customer Feedback Form Script - Interactivity & Client-side Validation
 */

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('publicFeedbackForm');
  if (!form) return;

  const ratingInput = document.getElementById('ratingInput');
  const starButtons = document.querySelectorAll('.star-btn');
  const ratingText = document.getElementById('ratingText');
  const messageInput = document.getElementById('feedbackMessage');
  const charCounter = document.getElementById('charCount');
  const resetBtn = document.getElementById('formResetBtn');

  const ratingDescriptions = {
    1: '1 Star - Terrible / Very Poor',
    2: '2 Stars - Poor / Disappointing',
    3: '3 Stars - Average / Neutral',
    4: '4 Stars - Very Good / Pleased',
    5: '5 Stars - Outstanding / Excellent'
  };

  // 1. Star Rating Hover & Selection Logic
  function updateStars(value) {
    starButtons.forEach(btn => {
      const btnVal = parseInt(btn.dataset.value, 10);
      if (btnVal <= value) {
        btn.classList.add('active');
        btn.innerHTML = '<i class="fa-solid fa-star"></i>';
      } else {
        btn.classList.remove('active');
        btn.innerHTML = '<i class="fa-regular fa-star"></i>';
      }
    });
    if (ratingText) {
      ratingText.textContent = ratingDescriptions[value] || `${value} Stars`;
    }
  }

  // Initialize with initial value
  let currentRating = parseInt(ratingInput.value, 10) || 5;
  updateStars(currentRating);

  starButtons.forEach(btn => {
    const val = parseInt(btn.dataset.value, 10);

    // Hover effect
    btn.addEventListener('mouseenter', () => {
      starButtons.forEach(b => {
        const bVal = parseInt(b.dataset.value, 10);
        if (bVal <= val) {
          b.classList.add('hovered');
          b.innerHTML = '<i class="fa-solid fa-star"></i>';
        } else {
          b.classList.remove('hovered');
          b.innerHTML = '<i class="fa-regular fa-star"></i>';
        }
      });
      if (ratingText) {
        ratingText.textContent = ratingDescriptions[val];
      }
    });

    // Mouse leave: revert to current active rating
    btn.addEventListener('mouseleave', () => {
      starButtons.forEach(b => b.classList.remove('hovered'));
      updateStars(currentRating);
    });

    // Click selection
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      currentRating = val;
      ratingInput.value = val;
      updateStars(currentRating);
    });
  });

  // 2. Character Counter for Feedback Message
  if (messageInput && charCounter) {
    const updateCharCount = () => {
      const len = messageInput.value.length;
      charCounter.textContent = `${len} characters (minimum 10 required)`;
      if (len >= 10) {
        charCounter.style.color = '#10B981';
      } else {
        charCounter.style.color = '#64748B';
      }
    };

    messageInput.addEventListener('input', updateCharCount);
    updateCharCount();
  }

  // 3. Client-side Validation Before Submit
  form.addEventListener('submit', function (e) {
    let isValid = true;
    const requiredInputs = form.querySelectorAll('[required]');

    // Clear previous invalid highlights
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

    // Check required fields
    requiredInputs.forEach(input => {
      if (!input.value.trim()) {
        input.classList.add('is-invalid');
        isValid = false;
      }
    });

    // Check email pattern
    const emailInput = document.getElementById('emailInput');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailInput && !emailRegex.test(emailInput.value.trim())) {
      emailInput.classList.add('is-invalid');
      isValid = false;
    }

    // Check message length
    if (messageInput && messageInput.value.trim().length < 10) {
      messageInput.classList.add('is-invalid');
      isValid = false;
    }

    if (!isValid) {
      e.preventDefault();
      // Scroll to first invalid field
      const firstInvalid = form.querySelector('.is-invalid');
      if (firstInvalid) {
        firstInvalid.focus();
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  });

  // Remove invalid style on input
  form.querySelectorAll('input, select, textarea').forEach(input => {
    input.addEventListener('input', () => {
      input.classList.remove('is-invalid');
    });
  });

  // 4. Form Reset Button
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      setTimeout(() => {
        currentRating = 5;
        ratingInput.value = 5;
        updateStars(5);
        if (messageInput && charCounter) {
          charCounter.textContent = '0 characters (minimum 10 required)';
          charCounter.style.color = '#64748B';
        }
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
      }, 50);
    });
  }
});
