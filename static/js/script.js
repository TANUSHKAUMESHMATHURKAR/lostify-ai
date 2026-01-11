document.addEventListener("DOMContentLoaded", () => {

  const lostEl = document.getElementById("lostCount");
  const foundEl = document.getElementById("foundCount");
  const matchEl = document.getElementById("matchCount");

  let lost = 0;
  let found = 0;
  let match = 0;

  document.querySelectorAll(".status.lost").forEach(() => lost++);
  document.querySelectorAll(".status.found").forEach(() => found++);
  document.querySelectorAll(".match-fill").forEach(el => {
  let randomMatch = Math.floor(Math.random() * (95 - 60 + 1)) + 60;
  el.innerText = randomMatch + "%";
  match = Math.max(match, randomMatch);
});


  animate(lostEl, lost);
  animate(foundEl, found);
  animate(matchEl, match, "%");

});

function animate(el, target, suffix = "") {
  let cur = 0;
  let step = Math.max(1, Math.ceil(target / 40));

  let i = setInterval(() => {
    cur += step;
    if (cur >= target) {
      cur = target;
      clearInterval(i);
    }
    el.innerText = cur + suffix;
  }, 30);
}
