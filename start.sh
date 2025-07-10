#!/usr/bin/env bash
set -e                              # Exit immediately on error

# Forward SIGTERM/SIGINT to both child processes
trap "echo 'Stopping…'; kill -TERM $(jobs -p); wait" TERM INT

echo "Launching FastAPI (or whatever is in start_server.py)…"
python start_server.py &

echo "Launching Streamlit UI…"
streamlit run streamlit_ui.py \
    --server.address 0.0.0.0 \
    --server.port    8501 \
    --server.headless true \
    --server.enableXsrfProtection false &

# Wait for either process to exit and propagate its status
wait -n
exit $?
