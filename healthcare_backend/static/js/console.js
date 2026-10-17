/**
 * CareOS Console Logic
 * Handles tab switching, KPI metric counts, CRUD for Patients, Doctors, and Mappings,
 * modal dialogs, and instant search.
 */

let state = {
  activeTab: 'patients',
  patients: [],
  doctors: [],
  mappings: [],
  currentUser: null,
  editingPatientId: null,
  editingDoctorId: null
};

document.addEventListener('DOMContentLoaded', () => {
  // Authentication Guard
  const token = getAccessToken();
  if (!token) {
    window.location.href = '/login/?next=/console/';
    return;
  }

  state.currentUser = getCurrentUser();
  renderUserInfo();
  initConsoleEvents();
  loadAllData();
});

function renderUserInfo() {
  const userNameElem = document.getElementById('user-display-name');
  const userAvatarElem = document.getElementById('user-avatar-initial');
  if (state.currentUser && userNameElem) {
    userNameElem.textContent = state.currentUser.name || state.currentUser.email;
    const initial = (state.currentUser.name || state.currentUser.email || 'U')[0].toUpperCase();
    if (userAvatarElem) userAvatarElem.textContent = initial;
  }
}

function initConsoleEvents() {
  // Signout button
  const signoutBtn = document.getElementById('btn-signout');
  if (signoutBtn) {
    signoutBtn.addEventListener('click', () => {
      clearAuthSession();
      showToast('Logged out successfully.', 'info');
      setTimeout(() => { window.location.href = '/login/'; }, 500);
    });
  }

  // Tab switching
  document.querySelectorAll('.console-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.console-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.style.display = 'none');

      btn.classList.add('active');
      const tabTarget = btn.getAttribute('data-tab');
      state.activeTab = tabTarget;
      const pane = document.getElementById(`tab-pane-${tabTarget}`);
      if (pane) pane.style.display = 'block';

      // Update toolbar Add button label
      updateAddButtonLabel(tabTarget);
    });
  });

  // Global Add button in toolbar
  const addBtn = document.getElementById('btn-toolbar-add');
  if (addBtn) {
    addBtn.addEventListener('click', () => {
      if (state.activeTab === 'patients') openPatientModal();
      else if (state.activeTab === 'doctors') openDoctorModal();
      else if (state.activeTab === 'mappings') openMappingModal();
    });
  }

  // Search input
  const searchInput = document.getElementById('global-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      filterCurrentTable(q);
    });
  }

  // Modal Close buttons
  document.querySelectorAll('.modal-close, .btn-modal-cancel').forEach(btn => {
    btn.addEventListener('click', closeAllModals);
  });

  // Patient Form Submit
  const patientForm = document.getElementById('patient-form');
  if (patientForm) {
    patientForm.addEventListener('submit', handlePatientSubmit);
  }

  // Doctor Form Submit
  const doctorForm = document.getElementById('doctor-form');
  if (doctorForm) {
    doctorForm.addEventListener('submit', handleDoctorSubmit);
  }

  // Mapping Form Submit
  const mappingForm = document.getElementById('mapping-form');
  if (mappingForm) {
    mappingForm.addEventListener('submit', handleMappingSubmit);
  }
}

function updateAddButtonLabel(tab) {
  const addBtn = document.getElementById('btn-toolbar-add');
  if (!addBtn) return;
  if (tab === 'patients') addBtn.textContent = '+ Add Patient';
  else if (tab === 'doctors') addBtn.textContent = '+ Add Doctor';
  else if (tab === 'mappings') addBtn.textContent = '+ Assign Doctor';
}

async function loadAllData() {
  await Promise.all([
    fetchPatients(),
    fetchDoctors(),
    fetchMappings(),
    fetchStats()
  ]);
}

async function fetchStats() {
  try {
    const res = await fetchWithAuth('/api/stats/');
    if (res.ok) {
      const data = await res.json();
      document.getElementById('kpi-total-patients').textContent = data.user_patients ?? state.patients.length;
      document.getElementById('kpi-total-doctors').textContent = data.total_doctors ?? state.doctors.length;
      document.getElementById('kpi-total-mappings').textContent = data.total_mappings ?? state.mappings.length;
      document.getElementById('kpi-system-status').textContent = data.system_status || 'Operational';
    }
  } catch (err) {
    console.warn('Stats fetch error:', err);
  }
}

// -------------------------------------------------------------
// PATIENTS CRUD
// -------------------------------------------------------------
async function fetchPatients() {
  const tbody = document.getElementById('patients-tbody');
  if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="skeleton-row"></td></tr>`;

  try {
    const res = await fetchWithAuth('/api/patients/');
    const data = await res.json();

    if (res.ok) {
      state.patients = data.results || data;
      renderPatientsTable(state.patients);
      document.getElementById('kpi-total-patients').textContent = state.patients.length;
    } else {
      showToast(data.message || 'Error fetching patients.', 'error');
    }
  } catch (err) {
    showToast('Failed to connect to patients API.', 'error');
  }
}

function renderPatientsTable(list) {
  const tbody = document.getElementById('patients-tbody');
  if (!tbody) return;

  if (list.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7">
          <div class="empty-state">
            <div class="empty-state-icon">📂</div>
            <h3>No patient records found</h3>
            <p>Click "Add Patient" to register a new patient in CareOS.</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = list.map(p => `
    <tr>
      <td class="mono font-bold">#${p.id}</td>
      <td><strong>${escapeHtml(p.name)}</strong></td>
      <td>${p.age} yrs · <span class="status-pill">${escapeHtml(p.gender)}</span></td>
      <td class="mono">${escapeHtml(p.phone)}</td>
      <td>${escapeHtml(p.address || '—')}</td>
      <td>${escapeHtml(p.medical_history || 'None noted')}</td>
      <td>
        <div class="action-buttons">
          <button class="btn-icon" title="Edit Patient" onclick="openPatientModal(${p.id})">✏️</button>
          <button class="btn-icon delete" title="Delete Patient" onclick="deletePatient(${p.id})">🗑️</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function openPatientModal(id = null) {
  clearFormErrors('patient-form');
  state.editingPatientId = id;
  const modal = document.getElementById('patient-modal');
  const title = document.getElementById('patient-modal-title');

  if (id) {
    const p = state.patients.find(item => item.id === id);
    if (!p) return;
    title.textContent = `Edit Patient #${id}`;
    document.getElementById('patient-name').value = p.name;
    document.getElementById('patient-age').value = p.age;
    document.getElementById('patient-gender').value = p.gender;
    document.getElementById('patient-phone').value = p.phone;
    document.getElementById('patient-address').value = p.address;
    document.getElementById('patient-medical-history').value = p.medical_history || '';
  } else {
    title.textContent = 'Add New Patient';
    document.getElementById('patient-form').reset();
  }

  modal.classList.add('open');
}

async function handlePatientSubmit(e) {
  e.preventDefault();
  clearFormErrors('patient-form');

  const payload = {
    name: document.getElementById('patient-name').value.trim(),
    age: parseInt(document.getElementById('patient-age').value),
    gender: document.getElementById('patient-gender').value,
    phone: document.getElementById('patient-phone').value.trim(),
    address: document.getElementById('patient-address').value.trim(),
    medical_history: document.getElementById('patient-medical-history').value.trim()
  };

  const isEdit = !!state.editingPatientId;
  const url = isEdit ? `/api/patients/${state.editingPatientId}/` : '/api/patients/';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    const res = await fetchWithAuth(url, {
      method,
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (res.ok && data.success) {
      showToast(isEdit ? 'Patient updated successfully.' : 'Patient created successfully.');
      closeAllModals();
      await fetchPatients();
      await fetchStats();
    } else {
      displayFormErrors('patient-form', data.errors);
      showToast(data.message || 'Validation error.', 'error');
    }
  } catch (err) {
    showToast('Failed to save patient record.', 'error');
  }
}

async function deletePatient(id) {
  if (!confirm(`Are you sure you want to delete patient #${id}? This action cannot be undone.`)) return;

  try {
    const res = await fetchWithAuth(`/api/patients/${id}/`, { method: 'DELETE' });
    const data = await res.json();

    if (res.ok && data.success) {
      showToast('Patient record deleted.');
      await fetchPatients();
      await fetchMappings();
      await fetchStats();
    } else {
      showToast(data.message || 'Cannot delete patient.', 'error');
    }
  } catch (err) {
    showToast('Network error deleting patient.', 'error');
  }
}

// -------------------------------------------------------------
// DOCTORS CRUD
// -------------------------------------------------------------
async function fetchDoctors() {
  const tbody = document.getElementById('doctors-tbody');
  if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="skeleton-row"></td></tr>`;

  try {
    const res = await fetchWithAuth('/api/doctors/');
    const data = await res.json();

    if (res.ok) {
      state.doctors = data.results || data;
      renderDoctorsTable(state.doctors);
      document.getElementById('kpi-total-doctors').textContent = state.doctors.length;
    }
  } catch (err) {
    showToast('Failed to fetch doctor directory.', 'error');
  }
}

function renderDoctorsTable(list) {
  const tbody = document.getElementById('doctors-tbody');
  if (!tbody) return;

  if (list.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7">
          <div class="empty-state">
            <div class="empty-state-icon">🩺</div>
            <h3>No doctors found in directory</h3>
            <p>Click "Add Doctor" to enroll a doctor into the network.</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = list.map(d => {
    const isOwner = state.currentUser && (d.created_by === state.currentUser.id || d.created_by_email === state.currentUser.email);
    return `
      <tr>
        <td class="mono font-bold">#${d.id}</td>
        <td><strong>Dr. ${escapeHtml(d.name)}</strong></td>
        <td><span class="api-chip get">${escapeHtml(d.specialization)}</span></td>
        <td>${escapeHtml(d.email)}</td>
        <td class="mono">${escapeHtml(d.phone)}</td>
        <td>${d.experience_years} years</td>
        <td>
          <div class="action-buttons">
            ${isOwner ? `
              <button class="btn-icon" title="Edit Doctor" onclick="openDoctorModal(${d.id})">✏️</button>
              <button class="btn-icon delete" title="Delete Doctor" onclick="deleteDoctor(${d.id})">🗑️</button>
            ` : `<span class="text-muted" style="font-size:0.75rem">Read Only</span>`}
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function openDoctorModal(id = null) {
  clearFormErrors('doctor-form');
  state.editingDoctorId = id;
  const modal = document.getElementById('doctor-modal');
  const title = document.getElementById('doctor-modal-title');

  if (id) {
    const d = state.doctors.find(item => item.id === id);
    if (!d) return;
    title.textContent = `Edit Doctor #${id}`;
    document.getElementById('doctor-name').value = d.name;
    document.getElementById('doctor-specialization').value = d.specialization;
    document.getElementById('doctor-email').value = d.email;
    document.getElementById('doctor-phone').value = d.phone;
    document.getElementById('doctor-experience').value = d.experience_years;
  } else {
    title.textContent = 'Add New Doctor';
    document.getElementById('doctor-form').reset();
  }

  modal.classList.add('open');
}

async function handleDoctorSubmit(e) {
  e.preventDefault();
  clearFormErrors('doctor-form');

  const payload = {
    name: document.getElementById('doctor-name').value.trim(),
    specialization: document.getElementById('doctor-specialization').value.trim(),
    email: document.getElementById('doctor-email').value.trim(),
    phone: document.getElementById('doctor-phone').value.trim(),
    experience_years: parseInt(document.getElementById('doctor-experience').value) || 0
  };

  const isEdit = !!state.editingDoctorId;
  const url = isEdit ? `/api/doctors/${state.editingDoctorId}/` : '/api/doctors/';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    const res = await fetchWithAuth(url, {
      method,
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (res.ok && data.success) {
      showToast(isEdit ? 'Doctor profile updated.' : 'Doctor enrolled successfully.');
      closeAllModals();
      await fetchDoctors();
      await fetchStats();
    } else {
      displayFormErrors('doctor-form', data.errors);
      showToast(data.message || 'Validation error.', 'error');
    }
  } catch (err) {
    showToast('Failed to save doctor profile.', 'error');
  }
}

async function deleteDoctor(id) {
  if (!confirm(`Are you sure you want to remove Doctor #${id}?`)) return;

  try {
    const res = await fetchWithAuth(`/api/doctors/${id}/`, { method: 'DELETE' });
    const data = await res.json();

    if (res.ok && data.success) {
      showToast('Doctor deleted successfully.');
      await fetchDoctors();
      await fetchMappings();
      await fetchStats();
    } else {
      showToast(data.message || 'Cannot delete doctor.', 'error');
    }
  } catch (err) {
    showToast('Network error deleting doctor.', 'error');
  }
}

// -------------------------------------------------------------
// MAPPINGS CRUD
// -------------------------------------------------------------
async function fetchMappings() {
  const tbody = document.getElementById('mappings-tbody');
  if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="skeleton-row"></td></tr>`;

  try {
    const res = await fetchWithAuth('/api/mappings/');
    const data = await res.json();

    if (res.ok) {
      state.mappings = data.results || data;
      renderMappingsTable(state.mappings);
      document.getElementById('kpi-total-mappings').textContent = state.mappings.length;
    }
  } catch (err) {
    showToast('Failed to fetch patient-doctor mappings.', 'error');
  }
}

function renderMappingsTable(list) {
  const tbody = document.getElementById('mappings-tbody');
  if (!tbody) return;

  if (list.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7">
          <div class="empty-state">
            <div class="empty-state-icon">🔗</div>
            <h3>No doctor assignments active</h3>
            <p>Click "Assign Doctor" to link a doctor to a patient record.</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = list.map(m => `
    <tr>
      <td class="mono font-bold">#${m.id}</td>
      <td><strong>${escapeHtml(m.patient_name || 'Patient #' + m.patient)}</strong></td>
      <td><strong>Dr. ${escapeHtml(m.doctor_name || 'Doctor #' + m.doctor)}</strong></td>
      <td><span class="api-chip post">${escapeHtml(m.doctor_specialization || 'Clinical')}</span></td>
      <td>${escapeHtml(m.assigned_by_name || 'Staff')}</td>
      <td class="mono" style="font-size:0.75rem">${new Date(m.created_at).toLocaleString()}</td>
      <td>
        <div class="action-buttons">
          <button class="btn-icon delete" title="Remove Assignment" onclick="deleteMapping(${m.id})">❌</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function openMappingModal() {
  clearFormErrors('mapping-form');
  const modal = document.getElementById('mapping-modal');
  const patientSelect = document.getElementById('mapping-patient-select');
  const doctorSelect = document.getElementById('mapping-doctor-select');

  // Populate patient options
  patientSelect.innerHTML = state.patients.length > 0
    ? state.patients.map(p => `<option value="${p.id}">#${p.id} - ${escapeHtml(p.name)} (${p.gender}, ${p.age}y)</option>`).join('')
    : `<option value="">No patients available (Create one first)</option>`;

  // Populate doctor options
  doctorSelect.innerHTML = state.doctors.length > 0
    ? state.doctors.map(d => `<option value="${d.id}">Dr. ${escapeHtml(d.name)} - ${escapeHtml(d.specialization)}</option>`).join('')
    : `<option value="">No doctors available</option>`;

  modal.classList.add('open');
}

async function handleMappingSubmit(e) {
  e.preventDefault();
  clearFormErrors('mapping-form');

  const patientId = document.getElementById('mapping-patient-select').value;
  const doctorId = document.getElementById('mapping-doctor-select').value;

  if (!patientId || !doctorId) {
    showToast('Please select both a patient and a doctor.', 'error');
    return;
  }

  const payload = {
    patient: parseInt(patientId),
    doctor: parseInt(doctorId)
  };

  try {
    const res = await fetchWithAuth('/api/mappings/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (res.ok && data.success) {
      showToast('Doctor assigned to patient successfully.');
      closeAllModals();
      await fetchMappings();
      await fetchStats();
    } else {
      displayFormErrors('mapping-form', data.errors);
      showToast(data.message || 'Mapping failed.', 'error');
    }
  } catch (err) {
    showToast('Failed to assign doctor.', 'error');
  }
}

async function deleteMapping(id) {
  if (!confirm(`Are you sure you want to remove doctor assignment #${id}?`)) return;

  try {
    const res = await fetchWithAuth(`/api/mappings/${id}/`, { method: 'DELETE' });
    const data = await res.json();

    if (res.ok && data.success) {
      showToast('Doctor assignment removed.');
      await fetchMappings();
      await fetchStats();
    } else {
      showToast(data.message || 'Cannot remove assignment.', 'error');
    }
  } catch (err) {
    showToast('Network error removing mapping.', 'error');
  }
}

// -------------------------------------------------------------
// FILTER & SEARCH
// -------------------------------------------------------------
function filterCurrentTable(query) {
  if (state.activeTab === 'patients') {
    const filtered = state.patients.filter(p =>
      p.name.toLowerCase().includes(query) ||
      p.phone.includes(query) ||
      (p.address && p.address.toLowerCase().includes(query))
    );
    renderPatientsTable(filtered);
  } else if (state.activeTab === 'doctors') {
    const filtered = state.doctors.filter(d =>
      d.name.toLowerCase().includes(query) ||
      d.specialization.toLowerCase().includes(query) ||
      d.email.toLowerCase().includes(query)
    );
    renderDoctorsTable(filtered);
  } else if (state.activeTab === 'mappings') {
    const filtered = state.mappings.filter(m =>
      (m.patient_name && m.patient_name.toLowerCase().includes(query)) ||
      (m.doctor_name && m.doctor_name.toLowerCase().includes(query)) ||
      (m.doctor_specialization && m.doctor_specialization.toLowerCase().includes(query))
    );
    renderMappingsTable(filtered);
  }
}

// -------------------------------------------------------------
// HELPERS
// -------------------------------------------------------------
function closeAllModals() {
  document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('open'));
  state.editingPatientId = null;
  state.editingDoctorId = null;
}

function clearFormErrors(formId) {
  const form = document.getElementById(formId);
  if (!form) return;
  form.querySelectorAll('.field-error').forEach(el => {
    el.textContent = '';
    el.classList.remove('active');
  });
}

function displayFormErrors(formId, errors) {
  if (!errors || typeof errors !== 'object') return;
  const form = document.getElementById(formId);
  if (!form) return;

  for (const [field, messages] of Object.entries(errors)) {
    const errorEl = form.querySelector(`.field-error[data-field="${field}"]`);
    if (errorEl) {
      errorEl.textContent = Array.isArray(messages) ? messages[0] : messages;
      errorEl.classList.add('active');
    }
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
