#  imports
import config
from DB import DB
import logging
from aiogram import Bot, Dispatcher, executor, types

# log level
logging.basicConfig(level=logging.INFO)

# bot init
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# db init
db = DB('botDB.db')

# cmds
@dp.message_handler(commands=['start', 'Start', 'START'])
@dp.message_handler(content_types=["new_chat_members"])
async def start(message: types.Message):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        db.addGroup(message.chat.id)
        if message.text == "/start":
            await message.answer('<b>Привіт!</b> Введіть команду "/help", щоб дізнатись, що я можу :).')
        else:
            for chat_member in message.new_chat_members:
                if not chat_member.is_bot:
                    if chat_member.username:
                        db.addUser(chat_member.id, chat_member.username, chat_member.first_name, message.chat.id)
                        await message.reply(f'{chat_member.first_name} додано до бази даних!')
                    else:
                        await message.reply(f"У користувача {chat_member.first_name} немає тега!")
                elif chat_member.username == config.BOT_USERNAME:
                    await message.answer('<b>Привіт!</b> Введіть команду "/help", щоб дізнатись, що я можу :).')
    else:
        await message.answer('<b>Привіт!</b> Мене створили для роботи у групових чатах. Використай команду "/help", щоб дізнатись більше!')

@dp.message_handler(content_types=["left_chat_member"])
async def member_left(message: types.Message):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if not message.left_chat_member.is_bot:
            db.deleteUser(message.left_chat_member.id, message.chat.id)
            await message.reply(f"Користувача {message.left_chat_member.first_name} видалено з бази даних :(")

@dp.message_handler(commands=['help', 'Help', 'HELP'])
async def help(message: types.Message):
    await message.answer(f"<b>Інструкція: </b>Після додання бота у групу необхідно заповнити базу даних користувачів. Для цього всім учасникам групи, доданим перед ботом, треба ввести комманду <b>'/addme'</b>.\n"
    f"Після цього користувачу стане доступний весь функціона бота:\n"
    f"<b>1) '/tagme' -</b> дозволити боту тегати учасника\n"
    f"<b>2) '/donttagme' -</b> заборонити боту тегати учасника\n"
    f"<b>3) '/changemytag' -</b> змінити тег користувача в базі даних на поточний\n"
    f"<b>4) '/deleteme' -</b> видалити користувача з бази даних\n"
    f"<b>5) '/all' -</b> тегнути всіх, хто дозволив боту це робити\n"
    f"<b>6) '/reallyall' -</b> тегнути усіх учасників групи без виключень\n"
    f"<b>7) '/showusers' -</b> показати дані користувачів, внесених до бази даних")

@dp.message_handler(commands=['addme', 'Addme', 'AddMe', 'addMe', 'addME', 'ADDME'])
async def addUser(message: types.Message):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if message.from_user.username:
            if db.addUser(message.from_user.id, message.from_user.username, message.from_user.first_name, message.chat.id):
                await message.reply(f'{message.from_user.first_name} додано в базу даних!')
            else:
                await message.reply("У базі :)")
        else:
            await message.reply(f"На жаль, у Вас, {message.from_user.first_name}, немає тега. Додайте його і введіть команду знову!")
    else:
        await message.answer("Ця команда доступна тільки у груповому чаті!")

@dp.message_handler(commands=['deleteme', 'Deleteme', 'DeleteMe', 'deleteMe', 'deleteMe', 'DELETEME'])
async def deleteUser(message: types.Message):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if db.userInGroupExists(message.from_user.id, message.chat.id):
            if message.from_user.username:
                if db.deleteUser(message.from_user.id, message.chat.id):
                    await message.reply(f'{message.from_user.first_name} видалено з бази даних!')
                else:
                    await message.reply("Вас не було у нашій базі :(")
            else:
                await message.reply(f"На жаль, у Вас, {message.from_user.first_name}, немає тега.")
        else:
            await message.reply("Вас немає у базі! Введіть команду '<b>/addme</b>' і спробуйте ще раз.")
    else:
        await message.answer("Ця команда доступна тільки у груповому чаті!")

@dp.message_handler(commands=['donttagme', 'DontTagMe', 'dontTagMe', 'DONTTAGME'])
async def dontTagUser(message: types.Message):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if db.userInGroupExists(message.from_user.id, message.chat.id):
            db.tagUser(message.from_user.id, message.chat.id, False)
            await message.reply('Oк')
        else:
            await message.reply("Вас немає у базі! Введіть команду '<b>/addme</b>' і спробуйте ще раз.")
    else:
        await message.answer("Ця команда доступна тільки у груповому чаті!")

@dp.message_handler(commands=['tagme', 'TagMe', 'tagMe', 'TAGME'])
async def tagUser(message: types.Message):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if db.userInGroupExists(message.from_user.id, message.chat.id):
            db.tagUser(message.from_user.id, message.chat.id, True)
            await message.reply('Oк')
        else:
            await message.reply("Вас немає у базі! Введіть команду '<b>/addme</b>' і спробуйте ще раз.")
    else:
        await message.answer("Ця команда доступна тільки у груповому чаті!")

@dp.message_handler(commands=['changemytag', 'ChangeMyTag', 'changeMyTag', 'CHANGEMYTAG'])
async def changeUserTag(message: types.Message):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if db.userInGroupExists(message.from_user.id, message.chat.id):
            db.changeUserTag(message.from_user.id, message.from_user.username)
            await message.answer('Тег змінено на ваш поточний')
        else:
            await message.reply("Вас немає у базі! Введіть команду '<b>/addme</b>' і спробуйте ще раз.")
    else:
        await message.answer("Ця команда доступна тільки у груповому чаті!")

@dp.message_handler(commands=['showusers'])
async def showAll(message: types.Message):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        users = db.getAllUsers(message.chat.id)
        if len(users) != 0:
            messg = ""
            i = 1
            for user in users:
                messg += f"{i}) Name: {user[3]}; tag: {user[2]}; permission to tag: {user[5]}\n"
                i += 1

            if messg != "":
                await message.reply(messg)
            else:
                await message.reply("На жаль, у базі даних нікого немає :(")
        else:
            await message.reply("На жаль, у базі даних нікого немає :(")
    else:
        await message.answer("Ця команда доступна тільки у груповому чаті!")

@dp.message_handler(commands=['reallyall', 'ReallyAll', 'reallyAll', 'REALLYALL'])
async def tagAll(message: types.Message):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if db.getUserTagsByGroupId(message.chat.id, True):
            mess = ""
            for i in db.getUserTagsByGroupId(message.chat.id, True):
                if i[0] != message.from_user.username:
                    mess += f"@{i[0]} "

            if mess == "":
                mess = "У базі даних нікого немає :("
            await message.answer(mess)
        else:
            await message.answer("У базі даних нікого немає :(")
    else:
        await message.answer("Ця команда доступна тільки у груповому чаті!")

@dp.message_handler(commands=['all', 'All', 'ALL'])
async def tagAvailableUsers(message: types.Message):
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if db.getUserTagsByGroupId(message.chat.id, False):
            mess = ""
            for i in db.getUserTagsByGroupId(message.chat.id, False):
                if i[0] != message.from_user.username:
                    mess += f"@{i[0]} "

            if mess == "":
                mess = "Вибачте, у базі даних поки що немає учасників, доступних для звернення!"
            await message.answer(mess)
        else:
            await message.answer("Вибачте, у базі даних поки що немає учасників, доступних для звернення!")
    else:
        await message.answer("Ця команда доступна тільки у груповому чаті!")

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = True)
    db.close()