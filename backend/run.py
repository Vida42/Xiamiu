import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"Starting Xiamiu API on {host}:{port} (debug mode: {debug})")
    print(f"Using database: {os.getenv('DB_NAME')} on {os.getenv('DB_HOST')}")
    
    # Run the application
    uvicorn.run("app.main:app", host=host, port=port, reload=debug)
