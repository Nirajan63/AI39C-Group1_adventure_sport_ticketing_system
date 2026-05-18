const $ = sel => document.querySelector(sel);

const avatarFile = $('#avatarFile');
const avatarImg = $('#avatarImg');
const coverFile = $('#coverFile');
const coverImg = $('#coverImg');

const saveBtn = $('#saveBtn');
const resetBtn = $('#resetBtn');
const deleteBtn = $('#deleteBtn');

function previewImage(file, target){
  if(!file) return;

  const reader = new FileReader();

  reader.onload = e => {
    target.src = e.target.result;
  };

  reader.readAsDataURL(file);
}

avatarFile.addEventListener('change', e => {
  previewImage(e.target.files[0], avatarImg);
});

coverFile.addEventListener('change', e => {
  previewImage(e.target.files[0], coverImg);
});

function saveProfile(){

  const profile = {
    firstName: $('#firstName').value,
    lastName: $('#lastName').value,
    email: $('#email').value,
    phone: $('#phone').value,
    city: $('#city').value,
    bio: $('#bio').value,
    language: $('#language').value,
    role: $('#role').value,
    avatar: avatarImg.src,
    cover: coverImg.src
  };

  localStorage.setItem(
    'thrillsphere_profile',
    JSON.stringify(profile)
  );

  $('#displayName').textContent =
    `${profile.firstName} ${profile.lastName}`;

  $('#displayRole').textContent =
    profile.role || 'Adventure Seeker';

  saveBtn.textContent = 'Saved ✓';

  setTimeout(() => {
    saveBtn.textContent = 'Save Profile';
  }, 1500);
}

function loadProfile(){

  const raw = localStorage.getItem('thrillsphere_profile');

  if(!raw) return;

  const p = JSON.parse(raw);

  $('#firstName').value = p.firstName || '';
  $('#lastName').value = p.lastName || '';
  $('#email').value = p.email || '';
  $('#phone').value = p.phone || '';
  $('#city').value = p.city || '';
  $('#bio').value = p.bio || '';
  $('#language').value = p.language || 'en';
  $('#role').value = p.role || '';

  if(p.avatar) avatarImg.src = p.avatar;
  if(p.cover) coverImg.src = p.cover;

  $('#displayName').textContent =
    `${p.firstName} ${p.lastName}`;

  $('#displayRole').textContent =
    p.role || 'Adventure Seeker';
}

function resetForm(){
  loadProfile();
}

function deleteProfile(){

  localStorage.removeItem('thrillsphere_profile');

  document.getElementById('profileForm').reset();

  location.reload();
}

saveBtn.addEventListener('click', saveProfile);
resetBtn.addEventListener('click', resetForm);
deleteBtn.addEventListener('click', deleteProfile);

window.addEventListener('load', () => {

  loadProfile();

  document.querySelectorAll('.glass').forEach((card, i) => {

    card.style.opacity = 0;
    card.style.transform = 'translateY(30px)';

    setTimeout(() => {

      card.style.transition = '.8s ease';

      card.style.opacity = 1;
      card.style.transform = 'translateY(0)';

    }, i * 200);
  });

});

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
