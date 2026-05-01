// authorization
const token = getToken();
if (!token) window.location.href = 'login.html';

const user = JSON.parse(localStorage.getItem('park_user') || 'null');
if (!user) window.location.href = 'login.html';

// fill ui
document.getElementById('chip-name').textContent = user.name ? user.name.split(' ')[0] : '-';
document.getElementById('chip-plate').textContent = user.plate || '-';
document.getElementById('d-name').textContent = user.name || '-';
document.getElementById('d-phone').textContent = user.phone || '-';
document.getElementById('d-plate').textContent = user.plate || '-';
document.getElementById('cc-plate').textContent = user.plate || '-';
document.getElementById('cc-name').textContent = user.name || '-';
document.getElementById('cc-phone').textContent = user.phone || '-';

// history
let tripHistory = JSON.parse(localStorage.getItem('park_history') || '[]');
let reserveStartTime = null;
let pendingSpot = null;

function saveHistory() {
  localStorage.setItem('park_history', JSON.stringify(tripHistory));
}

function formatDur(min) {
  if (min < 60) {
    return min + 'm';
  } else {
    return Math.floor(min/60) + 'h ' + (min%60) + 'm';
  }
}

function addTripToHistory(spot, durationMin) {
  const rateNum = parseFloat(spot.rate.replace(/[^0-9.]/g,''));
  const cost = parseFloat((rateNum * durationMin / 60).toFixed(2));
  const now = new Date();
  tripHistory.unshift({
    label: spot.floor + spot.row + spot.col,
    floor: spot.floor,
    type: spot.type,
    ev: spot.ev,
    rate: spot.rate,
    duration: durationMin,
    cost,
    date: now.toLocaleDateString('en', { month:'short', day:'numeric' }),
    time: now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0')
  });
  saveHistory();
  renderSidebarHistory();
  updateAvgStats();
}

function renderSidebarHistory() {
  const list = document.getElementById('history-list');
  if (!tripHistory.length) {
    list.innerHTML = '<div class="hist-empty">No trips yet.</div>';
    return;
  }
  list.innerHTML = tripHistory.slice(0,8).map(t => `
    <div class="hist-item">
      <div>
        <div class="hist-spot">${t.label}</div>
        <div class="hist-meta">Level ${t.floor} · ${t.type}${t.ev?' · EV':''}<br>${t.date} at ${t.time}</div>
      </div>
      <div>
        <div class="hist-cost">₸${Math.round(t.cost)}</div>
        <div class="hist-dur">${formatDur(t.duration)}</div>
      </div>
    </div>
  `).join('');
}

function updateAvgStats() {
  if (!tripHistory.length) return;
  const avgMin = Math.round(tripHistory.reduce((a,t) => a+t.duration, 0) / tripHistory.length);
  const avgCost = (tripHistory.reduce((a,t) => a+t.cost, 0) / tripHistory.length).toFixed(2);
  document.getElementById('avg-dur').textContent = formatDur(avgMin);
  document.getElementById('avg-cost').textContent = '₸' + avgCost;
  document.getElementById('total-trips').textContent = tripHistory.length;
  document.getElementById('avg-stats').style.display = 'flex';
}

async function loadSpots(floor) {
  try {
    let res = await apiGet('/api/spots?floor=' + floor);
    let data = await res.json();

    if (Array.isArray(data)) {
      data.forEach(function(s) {
        let id = s.floor + '_' + s.row + s.col;
        if (spots[id]) {
          spots[id].status = s.status;
        }
      });
    }
  } catch (e) {
    console.log('Could not load spots from API:', e);
  }

  renderMap();
  renderDetail();
}


function loadMyReservation() {
  const saved = localStorage.getItem('mySpot_' + user.plate);
  if (!saved) return;

  let s = JSON.parse(saved);

  mySpot = s;

  if (spots[mySpot.id]) {
    spots[mySpot.id].status = 'reserved';
  }

  document.getElementById('my-spot-badge').style.display = 'flex';
  document.getElementById('my-spot-id').textContent =
    mySpot.floor + mySpot.row + mySpot.col;
}

// spot detail
function renderDetail() {
  const pane = document.getElementById('detail-pane');

  if (mySpot && selectedSpot && selectedSpot.id === mySpot.id) {
    const s = mySpot;
    pane.innerHTML = `
      <div class="detail-num">${s.floor}${s.row}${s.col}</div>
      <div class="detail-sub"><div class="d-dot"></div>Your reservation${s.ev?' . EV':''}</div>
      <div class="meta-r"><span class="mk">Plate</span><span class="mv">${user.plate}</span></div>
      <div class="meta-r"><span class="mk">Rate</span><span class="mv">${s.rate}</span></div>
      <div class="meta-r"><span class="mk">Hold</span><span class="mv">15 min</span></div>
      <button class="btn-cancel-r" onclick="cancelRes()">Cancel reservation</button>`;
    return;
  }

  if (!selectedSpot) {
    pane.innerHTML = '<div class="detail-empty">Select a free spot on the map.</div>';
    return;
  }

  const s = selectedSpot;
  pane.innerHTML = `
    <div class="detail-num">${s.floor}${s.row}${s.col}</div>
    <div class="detail-sub"><div class="d-dot"></div>Available${s.ev?' . EV':''}</div>
    <div class="meta-r"><span class="mk">Floor</span><span class="mv">${s.floor}</span></div>
    <div class="meta-r"><span class="mk">Type</span><span class="mv">${s.type}</span></div>
    <div class="meta-r"><span class="mk">Rate</span><span class="mv">${s.rate}</span></div>
    <button class="btn-res" onclick="openModal()">Reserve</button>`;
}

function openModal() {
  if (!selectedSpot) return;
  pendingSpot = selectedSpot;
  const s = pendingSpot;
  document.getElementById('modal-b').innerHTML =
    `Spot <strong>${s.floor}${s.row}${s.col}</strong> for <strong>${user.plate}</strong>.<br><br>
     Driver: <strong>${user.name}</strong><br>
     Rate: <strong>${s.rate}</strong>${s.ev?' . EV charging':''}<br><br>
     Hold time: <strong>15 min</strong>.`;
  document.getElementById('overlay').classList.add('open');
}

function closeModal() {
  document.getElementById('overlay').classList.remove('open');
}

async function confirmRes() {
  closeModal();
  if (!pendingSpot) return;

  try {
    let spotId = pendingSpot.id; 
    let res = await apiPost('/api/spots/' + spotId + '/reserve', {}, true);

    if (res.ok) {
      localStorage.setItem('mySpot_' + user.plate, JSON.stringify(pendingSpot));
      if (mySpot) spots[mySpot.id].status = 'free';
      spots[pendingSpot.id].status = 'reserved';
      mySpot = pendingSpot;
      reserveStartTime = Date.now();
      document.getElementById('my-spot-badge').style.display = 'flex';
      document.getElementById('my-spot-id').textContent = mySpot.floor + mySpot.row + mySpot.col;
      addFeed(`<strong>${user.plate}</strong> reserved ${pendingSpot.floor}${pendingSpot.row}${pendingSpot.col}`);
      toast(`Reserved ${pendingSpot.floor}${pendingSpot.row}${pendingSpot.col}`);
      selectedSpot = pendingSpot;
      pendingSpot = null;
      renderMap();
      renderDetail();
    } else {
      let data = await res.json();
      toast(data.detail || 'Could not reserve');
      pendingSpot = null;
    }
  } catch (e) {
    toast('Server not available');
    pendingSpot = null;
  }
}

async function cancelRes() {
  if (!mySpot) return;

  try {
    let res = await apiDelete('/api/reservations/mine', true);

    if (res.ok) {
      localStorage.removeItem('mySpot_' + user.plate);
      const elapsed = reserveStartTime
        ? Math.max(1, Math.round((Date.now() - reserveStartTime) / 60000))
        : Math.floor(5 + Math.random() * 55);

      addTripToHistory(mySpot, elapsed);
      spots[mySpot.id].status = 'free';
      addFeed(`<strong>${user.plate}</strong> left - ${formatDur(elapsed)} at ${mySpot.floor}${mySpot.row}${mySpot.col}`);
      toast('Trip saved to history');
      document.getElementById('my-spot-badge').style.display = 'none';
      mySpot = null;
      selectedSpot = null;
      reserveStartTime = null;
      renderMap();
      renderDetail();
    } else {
      let data = await res.json();
      toast(data.detail || 'Could not cancel');
    }
  } catch (e) {
    toast('Server not available');
  }
}

// user menu
function toggleDrop() {
  document.getElementById('user-drop').classList.toggle('open');
}

function signOut() {
  removeToken();
  // localStorage.removeItem('park_user');

  window.location.href = 'login.html';
}

document.addEventListener('click', e => {
  if (!e.target.closest('#user-chip'))
    document.getElementById('user-drop').classList.remove('open');
});

// init

renderMap();      
renderDetail();
renderSidebarHistory();
updateAvgStats();
startClock();
loadSpots(currentFloor);  
loadMyReservation();