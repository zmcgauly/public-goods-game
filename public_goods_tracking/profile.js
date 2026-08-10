// OTAI SECTION: header

const guessData = {};

// OTAI SECTION: functions

function initializeProfileGuesses() {
  const sections = docQuerySelectorAllStrict('.profile-section');
  sections.forEach(section => {
    const targetId = eleQuerySelectorStrict(section, '.guess-age').dataset.target;
    guessData[targetId] = {};
  });
  
  docQuerySelectorAllStrict('.guess-age, .guess-race, .guess-gender, .guess-sexuality, .guess-ethnicity').forEach(input => {
    input.addEventListener('input', updateGuessData);
  });
  
  const form = closestStrict(docQuerySelectorStrict('#id_profile_guesses_json'), 'form');
  form.addEventListener('submit', saveGuessData);
}

function saveGuessData() {
  docQuerySelectorAllStrict('.profile-section').forEach(section => {
    const targetId = eleQuerySelectorStrict(section, '.guess-age').dataset.target;
    updateGuessDataForTarget(targetId);
  });
  const hiddenInput = docQuerySelectorStrict('#id_profile_guesses_json');
  hiddenInput.value = JSON.stringify(guessData);
}

function updateGuessData() {
  updateGuessDataForTarget(this.dataset.target);
}

function updateGuessDataForTarget(targetId) {
  const ageInput = docQuerySelectorStrict(`.guess-age[data-target="${targetId}"]`);
  const raceInput = docQuerySelectorStrict(`.guess-race[data-target="${targetId}"]`);
  const genderInput = docQuerySelectorStrict(`.guess-gender[data-target="${targetId}"]`);
  const sexualityInput = docQuerySelectorStrict(`.guess-sexuality[data-target="${targetId}"]`);
  const ethnicityInput = docQuerySelectorStrict(`.guess-ethnicity[data-target="${targetId}"]`);
  
  guessData[targetId] = {
    age: ageInput.value,
    ethnicity: ethnicityInput.value,
    race: raceInput.value,
    gender: genderInput.value,
    sexuality: sexualityInput.value
  };
}

// OTAI SECTION: footer

initializeProfileGuesses();
