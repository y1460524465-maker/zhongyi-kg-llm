@echo off
start /B streamlit run app.py --server.port 8501
start /B streamlit run app_stream.py --server.port 8502
echo Page 1 (normal): http://localhost:8501
echo Page 2 (stream): http://localhost:8502
pause
