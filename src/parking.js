// datas
const FLOORS = {
  A: { rows: ['A','B','C','D'], cols: 10 },
  B: { rows: ['A','B','C','D'], cols: 10 },
  C: { rows: ['A','B','C'], cols: 8 }
};

const EV_SPOTS = [
  'A_A1','A_A2','A_D9','A_D10',
  'B_B1','B_C10',
  'C_A7','C_A8'
];

function random(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

const spots = {};

for (let floor in FLOORS) {
  let config = FLOORS[floor];

  for (let i = 0; i < config.rows.length; i++) {
    let row = config.rows[i];

    for (let col = 1; col <= config.cols; col++) {
      let id = floor + "_" + row + col;

      spots[id] = {
        id: id,
        floor: floor,
        row: row,
        col: col,
        status: 'free',
        ev: EV_SPOTS.includes(id),
        type: random(['Compact','Standard','Standard','Large']),
        rate: "$" + (1.5 + Math.random() * 1.5).toFixed(1) + "/hr"
      };
    }
  }
}

let currentFloor = 'A';
let selectedSpot = null;
let mySpot = null;

function renderMap() {
  let wrap = document.getElementById('map-wrap');
  wrap.innerHTML = "";

  let cfg = FLOORS[currentFloor];

  let title = document.createElement('div');
  title.className = 'map-section-lbl';
  title.textContent = "Level " + currentFloor;
  wrap.appendChild(title);

  let block = document.createElement('div');
  block.className = 'grid-block';

  for (let i = 0; i < cfg.rows.length; i++) {
    let row = cfg.rows[i];

    if (i === 2) {
      let laneRow = document.createElement('div');
      laneRow.className = 'spot-row';

      let empty = document.createElement('div');
      empty.className = 'row-tag';
      laneRow.appendChild(empty);

      let gap = document.createElement('div');
      gap.className = 'lane-gap';
      laneRow.appendChild(gap);

      block.appendChild(laneRow);
    }

    let rowDiv = document.createElement('div');
    rowDiv.className = 'spot-row';

    let tag = document.createElement('div');
    tag.className = 'row-tag';
    tag.textContent = row;
    rowDiv.appendChild(tag);

    for (let col = 1; col <= cfg.cols; col++) {
      let id = currentFloor + "_" + row + col;
      let s = spots[id];

      let el = document.createElement('div');
      el.className = "spot " + s.status;

      if (mySpot && mySpot.id === id) {
        el.classList.add('mine');
      } else if (selectedSpot && selectedSpot.id === id) {
        el.classList.add('sel');
      }

      let sid = document.createElement('div');
      sid.className = 'sid';
      sid.textContent = row + col;
      el.appendChild(sid);

      if (s.ev) {
        let ev = document.createElement('div');
        ev.className = 'ev-pip';
        el.appendChild(ev);
      }

      if (s.status === 'free' || (mySpot && mySpot.id === id)) {
        el.onclick = function () {
          selectSpot(id);
        };
      }

      rowDiv.appendChild(el);

      if (col === Math.floor(cfg.cols / 2)) {
        let gap = document.createElement('div');
        gap.style.width = "14px";
        rowDiv.appendChild(gap);
      }
    }

    block.appendChild(rowDiv);
  }

  wrap.appendChild(block);
  updateCounts();
}

// выбор места типаа
function selectSpot(id) {
  selectedSpot = spots[id];
  renderMap();
  renderDetail();
}

// stats
function updateCounts() {
  let free = 0;

  let floors = {
    A: { f: 0, t: 0 },
    B: { f: 0, t: 0 },
    C: { f: 0, t: 0 }
  };

  for (let key in spots) {
    let s = spots[key];

    floors[s.floor].t++;

    if (s.status === 'free') {
      free++;
      floors[s.floor].f++;
    }
  }

  document.getElementById('n-free').textContent = free;

  for (let f in floors) {
    let data = floors[f];
    let percent = Math.round(((data.t - data.f) / data.t) * 100);

    document.getElementById("oc-" + f.toLowerCase()).style.width = percent + "%";
    document.getElementById("oc-" + f.toLowerCase() + "-p").textContent = percent + "%";
  }
}

// fake infos
const plates = ['001 NQZ 01','002 ALA 02','004 AKX 04','005 ALA 05','111 KZO 11'];

function randomSpot() {
  let f = random(['A','B','C']);
  let cfg = FLOORS[f];

  return f + random(cfg.rows) + Math.ceil(Math.random() * cfg.cols);
}

function addFeed(text) {
  let feed = document.getElementById('feed');

  let d = new Date();
  let time =
    d.getHours().toString().padStart(2,'0') + ":" +
    d.getMinutes().toString().padStart(2,'0');

  let item = document.createElement('div');
  item.className = 'feed-item';
  item.innerHTML = "<div class='ft'>" + text + "</div><div class='fts'>" + time + "</div>";

  feed.prepend(item);

  if (feed.children.length > 7) {
    feed.removeChild(feed.lastChild);
  }
}

function autoFeed() {
  let enter = Math.random() > 0.4;
  let plate = random(plates);
  let spot = randomSpot();

  if (enter) {
    addFeed("<strong>" + plate + "</strong> entered " + spot);
  } else {
    addFeed("<strong>" + plate + "</strong> left " + spot);
  }

  if (Math.random() > 0.45) {
    let keys = Object.keys(spots);
    let k = keys[Math.floor(Math.random() * keys.length)];

    if (!mySpot || mySpot.id !== k) {
      spots[k].status = enter ? 'occupied' : 'free';

      if (currentFloor === spots[k].floor) {
        renderMap();
      } else {
        updateCounts();
      }
    }
  }
}

// clock
function startClock() {
  function update() {
    let d = new Date();

    document.getElementById('clock').textContent =
      d.getHours().toString().padStart(2,'0') + ":" +
      d.getMinutes().toString().padStart(2,'0') + ":" +
      d.getSeconds().toString().padStart(2,'0');
  }

  update();
  setInterval(update, 1000);
}

// toast
function toast(msg) {
  let t = document.getElementById('toast');

  t.textContent = msg;
  t.classList.add('show');

  setTimeout(function () {
    t.classList.remove('show');
  }, 2500);
}

// tabss
function switchTab(name, btn) {
  let tabs = document.querySelectorAll('.sb-tab');
  let panels = document.querySelectorAll('.tab-panel');

  tabs.forEach(function (b) {
    b.classList.remove('active');
  });

  panels.forEach(function (p) {
    p.classList.remove('show');
  });

  btn.classList.add('active');
  document.getElementById("tab-" + name).classList.add('show');
}

// changing floors
document.getElementById('floor-nav').addEventListener('click', function (e) {
  let btn = e.target.closest('.floor-btn');
  if (!btn) return;

  currentFloor = btn.dataset.floor;
  selectedSpot = null;

  document.querySelectorAll('.floor-btn').forEach(function (b) {
    b.classList.remove('active');
  });

  btn.classList.add('active');

  renderMap();
  renderDetail();
});

// хззз работаетт
