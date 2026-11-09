## 2026-11-09 - Streamlit Execution Model & Caching
**Learning:** Streamlit executes the entire Python script from top to bottom on *every* user interaction (button click, text input, etc). Placing external blocking network calls (like fetching local telemetry on port 9400) directly in the rendering flow without caching causes severe UI stuttering and redundant network traffic on every event.
**Action:** Always wrap external data fetching in `@st.cache_data(ttl=X)` to decouple slow I/O from Streamlit's rapid re-render cycle, preventing the main thread from blocking.
