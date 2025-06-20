from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

class Review(BaseModel):
    rating: int = Field(..., gt=0, lt=6, description="Rating from 1 to 5")
    comment: str

class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    reviews: List[Review] = []
    is_favorite: bool = False

class BookCreate(BaseModel):
    title: str
    author: str
    genre: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

books_db = [
    Book(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald", genre="Classic", reviews=[Review(rating=5, comment="A masterpiece!")]),
    Book(id=2, title="To Kill a Mockingbird", author="Harper Lee", genre="Classic", reviews=[Review(rating=5, comment="Incredible book.")])
]
next_book_id = 3

@app.get("/books", response_model=List[Book])
async def get_books():
    return books_db

@app.post("/books", response_model=Book, status_code=201)
async def add_book(book_create: BookCreate):
    global next_book_id
    new_book = Book(
        id=next_book_id,
        title=book_create.title,
        author=book_create.author,
        genre=book_create.genre
    )
    books_db.append(new_book)
    next_book_id += 1
    return new_book

@app.post("/books/{book_id}/reviews", response_model=Book)
async def add_review_to_book(book_id: int, review: Review):
    for book in books_db:
        if book.id == book_id:
            book.reviews.append(review)
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books/favorites", response_model=List[Book])
async def get_favorite_books():
    return [book for book in books_db if book.is_favorite]

@app.post("/books/{book_id}/favorite", response_model=Book)
async def mark_book_as_favorite(book_id: int):
    for book in books_db:
        if book.id == book_id:
            book.is_favorite = True
            return book
    raise HTTPException(status_code=404, detail="Book not found") 