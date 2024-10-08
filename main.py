from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": """
.______       _______   ______  _______ .______        ___      
|   _  \     |   ____| /      ||   ____||   _  \      /   \     
|  |_)  |    |  |__   |  ,----'|  |__   |  |_)  |    /  ^  \    
|      /     |   __|  |  |     |   __|  |   _  <    /  /_\  \   
|  |\  \----.|  |____ |  `----.|  |____ |  |_)  |  /  _____  \  
| _| `._____||_______| \______||_______||______/  /__/     \__\ 
            """}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
