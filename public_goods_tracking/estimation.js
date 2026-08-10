// OTAI SECTION: header


const ballsPerTarget = {};
const maxBalls = js_vars.BALLS_PER_ESTIMATE;


// OTAI SECTION: functions

function addBall(targetId, amount) {
  
  if (!ballsPerTarget[targetId][amount]) {
    ballsPerTarget[targetId][amount] = 0;
  }
  const totalBalls = Object.values(ballsPerTarget[targetId]).reduce((a, b) => a + b, 0);
  if (totalBalls >= maxBalls) {
    return;
  }
  ballsPerTarget[targetId][amount]++;
  renderBallStack(targetId, amount);
  updateBallsRemaining(targetId);
  saveEstimateData();
  
}

function initializeEstimation() {
  
  const sections = docQuerySelectorAllStrict('.estimation-section');
  sections.forEach(section => {
    const targetId = eleQuerySelectorStrict(section, '.contribution-slots').dataset.targetId;
    ballsPerTarget[targetId] = {};
  });
  
  docQuerySelectorAllStrict('.btn-add-ball').forEach(btn => {
    btn.addEventListener('click', () => {
      addBall(btn.dataset.target, btn.dataset.amount);
    });
  });
  
  docQuerySelectorAllStrict('.btn-remove-ball').forEach(btn => {
    btn.addEventListener('click', () => {
      removeBall(btn.dataset.target, btn.dataset.amount);
    });
  });
  
}

function removeBall(targetId, amount) {
  
  if (!ballsPerTarget[targetId][amount] || ballsPerTarget[targetId][amount] === 0) {
    return;
  }
  ballsPerTarget[targetId][amount]--;
  renderBallStack(targetId, amount);
  updateBallsRemaining(targetId);
  saveEstimateData();
  
}

function renderBallStack(targetId, amount) {
  
  const count = ballsPerTarget[targetId][amount] || 0;
  const stackEl = docQuerySelectorStrict(`#slot-${targetId}-${amount}`);
  const countEl = docQuerySelectorStrict(`#slot-count-${targetId}-${amount}`);
  stackEl.innerHTML = '';
  stackEl.setAttribute('aria-label', `${count} balls`);
  countEl.textContent = count;
  for (let i = 0; i < count; i++) {
    const ballEl = document.createElement('div');
    ballEl.className = 'stack-ball';
    stackEl.appendChild(ballEl);
  }
  
}

function saveEstimateData() {
  
  for (const targetId in ballsPerTarget) {
    const hiddenInput = docQuerySelectorStrict(`#estimate-data-${targetId}`);
    hiddenInput.value = JSON.stringify(ballsPerTarget[targetId]);
  }
  
}

function updateBallsRemaining(targetId) {
  
  const totalUsed = Object.values(ballsPerTarget[targetId]).reduce((a, b) => a + b, 0);
  const remaining = maxBalls - totalUsed;
  const remainingEl = docQuerySelectorStrict(`#balls-remaining-${targetId}`);
  remainingEl.textContent = remaining;
  
}

// OTAI SECTION: footer


initializeEstimation();
