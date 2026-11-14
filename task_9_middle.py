from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def index():
    students = [
        {"name": "Иван", "grade": 5},
        {"name": "Анна", "grade": 4},
        {"name": "Максим", "grade": 5},
        {"name": "Елена", "grade": 3}
    ]

    return render_template(
        "task_9.html",
        title="Успеваемость студентов",
        students=students
    )


if __name__ == "__main__":
    app.run(port=5000)
