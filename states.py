from aiogram.fsm.state import StatesGroup, State

class QuizState(StatesGroup):
    choosing_language = State()
    answering = State()

class AdminState(StatesGroup):
    adding_sponsor = State()
    removing_sponsor = State()