// Read args from Python
const { total_bullish, total_bearish, default_bullish, default_bearish } = window.streamlitWidgetArgs;

let state = { buy: default_bullish, sell: default_bearish };

function initSlider(trackId, fillId, thumbId, valueId, min, max, key) {
  const track = document.getElementById(trackId);
  const fill = document.getElementById(fillId);
  const thumb = document.getElementById(thumbId);
  const valueEl = document.getElementById(valueId);

  let dragging = false;

  const updateUI = (val) => {
    const pct = ((val - min) / (max - min)) * 100;
    fill.style.width = pct + "%";
    thumb.style.left = pct + "%";
    valueEl.textContent = val;
  };

  const setVal = (clientX) => {
    const rect = track.getBoundingClientRect();
    let ratio = (clientX - rect.left) / rect.width;
    ratio = Math.max(0, Math.min(1, ratio));
    const val = Math.round(min + ratio * (max - min));
    state[key] = val;
    updateUI(val);
  };

  track.addEventListener("mousedown", e => { dragging = true; setVal(e.clientX); });
  window.addEventListener("mousemove", e => { if (dragging) setVal(e.clientX); });
  window.addEventListener("mouseup", () => {
    if (dragging) {
      dragging = false;
      Streamlit.setComponentValue([state.buy, state.sell]);
    }
  });

  track.addEventListener("touchstart", e => { dragging = true; setVal(e.touches[0].clientX); }, { passive: false });
  window.addEventListener("touchmove", e => { if (dragging) setVal(e.touches[0].clientX); }, { passive: false });
  window.addEventListener("touchend", () => {
    if (dragging) {
      dragging = false;
      Streamlit.setComponentValue([state.buy, state.sell]);
    }
  });

  updateUI(state[key]);
}

// Wait for Streamlit to load
window.streamlitEvents.addEventListener(Streamlit.RENDER_EVENT, () => {
  initSlider("buy-track", "buy-fill", "buy-thumb", "buy-value", 1, total_bullish, "buy");
  initSlider("sell-track", "sell-fill", "sell-thumb", "sell-value", 1, total_bearish, "sell");
  Streamlit.setFrameHeight();
});

Streamlit.setComponentValue([state.buy, state.sell]);
