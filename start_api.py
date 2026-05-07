"""
Run this to start the FastAPI REST backend for the React frontend.
The Gradio app runs on port 7862; this API runs on port 8000.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("aarogya.api:app", host="127.0.0.1", port=8000, reload=True)
