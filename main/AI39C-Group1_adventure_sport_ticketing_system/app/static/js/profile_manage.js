const $ = sel => document.querySelector(sel);

const avatarFile = $('#avatarFile');
const avatarImg = $('#avatarImg');
const coverFile = $('#coverFile');
const coverImg = $('#coverImg');

const saveBtn = $('#saveBtn');
const resetBtn = $('#resetBtn');
const deleteBtn = $('#deleteBtn');

// Helper to convert uploaded files to base64 preview strings
function previewImage(file, target){
  if(!file) return;

  const reader = new FileReader();

  reader.onload = e => {
    target.src = e.target.result;
  };

  reader.readAsDataURL(file);
}

if (avatarFile) {
  avatarFile.addEventListener('change', e => {
    previewImage(e.target.files[0], avatarImg);
  });
}

if (coverFile) {
  coverFile.addEventListener('change', e => {
    previewImage(e.target.files[0], coverImg);
  });
}

// Asynchronously save profile fields and system theme preferences to MySQL
async function saveProfile(){
  saveBtn.disabled = true;
  saveBtn.textContent = 'Saving...';

  const themePreference = $('#themePreference').value;

  const profile = {
    firstName: $('#firstName').value.strip ? $('#firstName').value.strip() : $('#firstName').value.trim(),
    lastName: $('#lastName').value.strip ? $('#lastName').value.strip() : $('#lastName').value.trim(),
    email: $('#email').value.trim(),
    phone: $('#phone').value.trim(),
    city: $('#city').value.trim(),
    bio: $('#bio').value,
    language: $('#language').value,
    role: $('#role').value.trim(),
    avatar: avatarImg.src,
    cover: coverImg.src,
    theme_preference: themePreference
  };

  try {
    const response = await fetch('/manage', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(profile)
    });

    const data = await response.json();

    if (response.ok) {
      // Keep localStorage fallback in sync
      localStorage.setItem('thrillsphere_profile', JSON.stringify(profile));
      localStorage.setItem('theme', themePreference);

      // Reactively apply theme to Document body instantly without page refresh
      if (themePreference === 'dark') {
        document.documentElement.classList.add('dark-mode');
        // Update header theme icon to Sun if visible
        const headerIcon = document.querySelector('#theme-toggle i');
        if (headerIcon) headerIcon.className = 'bx bx-sun';
      } else {
        document.documentElement.classList.remove('dark-mode');
        const headerIcon = document.querySelector('#theme-toggle i');
        if (headerIcon) headerIcon.className = 'bx bx-moon';
      }

      // Sync display metadata
      $('#displayName').textContent = `${profile.firstName} ${profile.lastName}`;
      $('#displayRole').textContent = profile.role || 'Adventure Seeker';

      saveBtn.textContent = 'Saved ✓';
      saveBtn.style.background = '#00c878';
    } else {
      alert(data.message || 'Failed to save profile on the database server.');
      saveBtn.textContent = 'Save Profile';
    }
  } catch (err) {
    console.error("Save profile error:", err);
    alert('Failed to connect to the server.');
    saveBtn.textContent = 'Save Profile';
  } finally {
    saveBtn.disabled = false;
    setTimeout(() => {
      saveBtn.style.background = '';
      saveBtn.textContent = 'Save Profile';
    }, 2000);
  }
}

// Reset form elements to latest database-saved parameters
function resetForm(){
  location.reload();
}

// Clear profile cache
function deleteProfile(){
  if(confirm("Are you sure you want to clear your local profile cache? This does not delete your main login account.")) {
    localStorage.removeItem('thrillsphere_profile');
    location.reload();
  }
}

if (saveBtn) saveBtn.addEventListener('click', saveProfile);
if (resetBtn) resetBtn.addEventListener('click', resetForm);
if (deleteBtn) deleteBtn.addEventListener('click', deleteProfile);

window.addEventListener('load', () => {
  // Fade in animation of container elements on load
  document.querySelectorAll('.glass').forEach((card, i) => {
    card.style.opacity = 0;
    card.style.transform = 'translateY(30px)';

    setTimeout(() => {
      card.style.transition = '.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
      card.style.opacity = 1;
      card.style.transform = 'translateY(0)';
    }, i * 200);
  });
});

// Dynamic Ripple Effect on save buttons click
document.querySelectorAll('.btn').forEach(btn => {
  btn.addEventListener('click', function(e){
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    const rect = this.getBoundingClientRect();
    ripple.style.left = `${e.clientX - rect.left}px`;
    ripple.style.top = `${e.clientY - rect.top}px`;
    this.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });
});
