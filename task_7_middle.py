import uvicorn
from fastapi import FastAPI


app = FastAPI(title="Лабораторная работа №6")


@app.get("/info")
def get_info():
    return {
        "message": "Привет из FastAPI",
        "variant": 7,
        "task": 7
    }


def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
