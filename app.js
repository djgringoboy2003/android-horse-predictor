async function loadRaces() {
  const container = document.getElementById("races");
  container.innerHTML = '<div class="race">Loading racecards...</div>';

  try {
    const res = await fetch("data/upcoming_races.json?t=" + Date.now());
    const meetings = await res.json();
    container.innerHTML = "";

    if (!Array.isArray(meetings) || meetings.length === 0) {
      container.innerHTML = '<div class="race">No racecards found yet.</div>';
      return;
    }

    meetings.forEach(meeting => {
      const card = document.createElement("div");
      card.className = "race";

      const h2 = document.createElement("h2");
      h2.textContent = meeting.meeting;
      card.appendChild(h2);

      const meta = document.createElement("div");
      meta.textContent = `Going: ${meeting.going || "-"} | Surface: ${meeting.surface || "-"}`;
      card.appendChild(meta);

      meeting.races.forEach(race => {
        const row = document.createElement("div");
        row.className = "horse";
        row.style.display = "block";
        row.style.marginTop = "10px";
        row.innerHTML =
          `<div><strong>${race.time}</strong> ${race.title}</div>` +
          `<div>${race.age_band || "-"} | ${race.class || "-"} | ${race.distance || "-"} | ${race.runner_count ?? "-"} runners</div>`;
        card.appendChild(row);
      });

      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = `<div class="race">Error loading racecards: ${err.message}</div>`;
  }
}

loadRaces();
