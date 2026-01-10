function launchConfetti() {
  const duration = 1200;
  const end = Date.now() + duration;

  (function frame() {
    confetti({
      particleCount: 6,
      spread: 70,
      origin: { x: Math.random(), y: Math.random() - 0.2 }
    });

    if (Date.now() < end) {
      requestAnimationFrame(frame);
    }
  })();
}
