
## 2024-11-10 - Streamlit Request Caching & Exception Masking
**Learning:** In Streamlit, all code runs synchronously on each UI interaction. Network calls (like fetching DCGM telemetry) without `@st.cache_data` lock up the render loop. Also, exposing raw exceptions (via `st.error(e)`) leaks internals to users. Code running on script import also prevents safe unit testing unless logic is wrapped inside an `if __name__ == "__main__":` block.
**Action:** Extract network requests into separate functions, cache them using `@st.cache_data(ttl=X)`, handle exceptions with `logging.error(..., exc_info=True)` returning generic messages, and move Streamlit layout code into a `main()` function to enable unit testing.
