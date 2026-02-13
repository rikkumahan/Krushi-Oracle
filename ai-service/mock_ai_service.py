
from fastapi import FastAPI, Request
import uvicorn
import logging
import sys

# Configure logging to write to a file
logging.basicConfig(
    filename='request_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    force=True
)

app = FastAPI()

@app.post("/api/ideas/generate")
@app.post("/api/v2/score-idea")
async def capture_request(request: Request):
    headers = dict(request.headers)
    body = await request.body()
    
    log_message = f"""
    --- RECEIVED REQUEST ---
    URL: {request.url}
    Method: {request.method}
    Headers: {headers}
    Body: {body.decode(errors='replace')}
    ------------------------
    """
    logging.info(log_message)
    print(log_message) # Print to stdout as well
    sys.stdout.flush()
    
    return {"message": "Mock received", "status": "success"}

if __name__ == "__main__":
    # Run on port 8002 as configured in Java app
    uvicorn.run(app, host="127.0.0.1", port=8002)
