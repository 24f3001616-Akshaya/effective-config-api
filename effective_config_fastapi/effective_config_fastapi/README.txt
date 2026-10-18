Effective Config FastAPI assignment starter

Run locally:
  python -m pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port 8000

For Render:
1. Upload these files to a GitHub repository.
2. Create a Render Web Service connected to that repository.
3. Build command: pip install -r requirements.txt
4. Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
5. Add environment variables in Render:
   APP_DEBUG=true
   APP_LOG_LEVEL=error
   APP_API_KEY=key-71fo7mitwj
   APP_PORT=8000
   APP_WORKERS=2
6. Deploy, test /effective-config, and submit its public URL.

The app masks api_key in every response.
