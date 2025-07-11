from aiogram.fsm.state import State, StatesGroup


class RequestFSM(StatesGroup):
    brand = State()
    model = State()
    color_code = State()
    vin = State()
    year = State()
    image = State()  # Состояние для загрузки изображения
    phone = State()
    address = State()
    notes = State()
    confirm = State()


class AdminFSM(StatesGroup):
    search_phone = State()  # Состояние для поиска по номеру телефона


class PriceFSM(StatesGroup):
    add_title = State()
    add_description = State()
    add_price = State()
    edit_title = State()
    edit_description = State()
    edit_price = State()
