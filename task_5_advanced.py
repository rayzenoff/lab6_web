import sqlite3
from contextlib import asynccontextmanager, closing
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator


DB_PATH = Path(__file__).with_name("notes.db")


class NoteInput(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=1000)

    @field_validator("title", "content")
    @classmethod
    def validate_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Поле не может быть пустым")
        return value


class Note(NoteInput):
    id: int


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    with closing(get_connection()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()
    yield


app = FastAPI(
    title="REST API для заметок",
    lifespan=lifespan
)


@app.get("/notes", response_model=list[Note])
def get_notes():
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT id, title, content FROM notes ORDER BY id"
        ).fetchall()

    return [dict(row) for row in rows]


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT id, title, content FROM notes WHERE id = ?",
            (note_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Заметка не найдена"
        )

    return dict(row)


@app.post("/notes", response_model=Note, status_code=201)
def create_note(note: NoteInput):
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (note.title, note.content)
        )
        conn.commit()
        note_id = cursor.lastrowid

    return Note(id=note_id, **note.model_dump())


@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteInput):
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            """
            UPDATE notes
            SET title = ?, content = ?
            WHERE id = ?
            """,
            (note.title, note.content, note_id)
        )
        conn.commit()
        updated = cursor.rowcount

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Заметка не найдена"
        )

    return Note(id=note_id, **note.model_dump())


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,)
        )
        conn.commit()
        deleted = cursor.rowcount

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Заметка не найдена"
        )


def main():
    uvicorn.run(app, host="127.0.0.1", port=8002)


if __name__ == "__main__":
    main()
