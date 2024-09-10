from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

start_board = ReplyKeyboardMarkup(resize_keyboard=True)
start_board.add('Запустить помошника')

admin_board = ReplyKeyboardMarkup(resize_keyboard=True)
admin_board.add('Запустить помошника').add('Информация о личности').add('Сборос настроек').add('Информация о пользователях')

main_board = InlineKeyboardMarkup(row_width=2)
main_board.add(InlineKeyboardButton(text='Запуск помощника', callback_data='start'),
               InlineKeyboardButton(text='Указание личности', callback_data='com_person'),
               InlineKeyboardButton(text='Информация о личности', callback_data='info'),
               InlineKeyboardButton(text='Сброс параметров', callback_data='reset'))

exit_board = ReplyKeyboardMarkup(resize_keyboard=True)
exit_board.add('В главное меню')
