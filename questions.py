import random

QUESTIONS = {
    "Python": [
        {
            "question": "Что делает функция len()?",
            "options": ["Возвращает длину объекта", "Удаляет элемент", "Сортирует список", "Проверяет тип данных"],
            "answer": 0
        },
        {
            "question": "Как создать список в Python?",
            "options": ["{}", "[]", "()", "<>"],
            "answer": 1
        },
        {
            "question": "Какой оператор используется для возведения в степень?",
            "options": ["^", "**", "*", "//"],
            "answer": 1
        },
        {
            "question": "Что выведет print(2 * '3')?",
            "options": ["6", "'33'", "33", "Ошибка"],
            "answer": 2
        },
        {
            "question": "Как получить тип переменной?",
            "options": ["type()", "typeof()", "get_type()", "var_type()"],
            "answer": 0
        }
    ],
    "JavaScript": [
        {
            "question": "Как объявить переменную в JavaScript?",
            "options": ["var", "int", "string", "define"],
            "answer": 0
        },
        {
            "question": "Что выведет console.log(typeof [])?",
            "options": ["array", "object", "undefined", "list"],
            "answer": 1
        },
        {
            "question": "Какой метод добавляет элемент в конец массива?",
            "options": ["push()", "pop()", "shift()", "unshift()"],
            "answer": 0
        }
    ],
    "HTML/CSS": [
        {
            "question": "Какой тег создает ссылку?",
            "options": ["<a>", "<p>", "<div>", "<link>"],
            "answer": 0
        },
        {
            "question": "Какой CSS-селектор выбирает элемент по id?",
            "options": [".id", "#id", "id", "*id"],
            "answer": 1
        },
        {
            "question": "Какой тег используется для изображений?",
            "options": ["<img>", "<pic>", "<image>", "<src>"],
            "answer": 0
        }
    ]
}

def get_random_questions(language):
    """Возвращает случайные вопросы для выбранного языка"""
    questions = QUESTIONS.get(language, [])
    if not questions:
        return []
    count = min(5, len(questions)) 
    return random.sample(questions, count)