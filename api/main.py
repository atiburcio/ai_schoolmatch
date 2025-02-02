from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.book_comparison_agent import BookComparisonAgent
from models.book import Book

app = FastAPI(title="Book Comparison Agent API")
agent = BookComparisonAgent()

class ComparisonRequest(BaseModel):
    request: str

class BookSubmission(BaseModel):
    book: Book

@app.post("/compare")
async def compare_books(request: ComparisonRequest):
    try:
        results = agent.process_request(request.request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/books")
async def add_book(submission: BookSubmission):
    try:
        agent.vector_store.add_book(submission.book)
        return {"message": "Book added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
