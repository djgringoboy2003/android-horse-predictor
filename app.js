async function loadRaces() {
  const container = document.getElementById('races');
  container.innerHTML = '<div class="race">Loading races...</div>';

  try {
    const res = await fetch('data/upcoming_races.json?t=' + Date.now());
    if (!res.ok) {
      throw new Error('Failed to load race data');
    }

    const races = await res.json();
    container.innerHTML = '';

    if (!Array.isArray(races) || races.length === 0) {
      container.innerHTML = '<div class="race">No race data found yet. Run the Update race data workflow, then refresh this page.</div>';
      return;
    }

    races.forEach(race => {
      const div = document.createElement('div');
      div.className = 'race';

      const title = document.createElement('h3');
      title.innerText = `${race.time} ${race.course}`;
      div.appendChild(title);

      const subtitle = document.createElement('div');
      subtitle.innerText = race.day || '';
      div.appendChild(subtitle);

      race.runners.sort((a, b) => b.implied_prob - a.implied_prob);

      race.runners.forEach((r, index) => {
        const row = document.createElement('div');
        row.className = 'horse';
        if (index === 0) row.classList.add('top');
        row.innerHTML = `<span>${index + 1}. ${r.horse} (${r.odds})</span><span>${(r.implied_prob * 100).toFixed(1)}%</span>`;
        div.appendChild(row);
      });

      container.appendChild(div);
    });
  } catch (err) {
    container.innerHTML = `<div class="race">Error loading races: ${err.message}</div>`;
  }
}

loadRaces();
