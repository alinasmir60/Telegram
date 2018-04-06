from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import requests, random


def start(bot, update, user_data):
    user_data["lang"] = "ru-en"
    update.message.reply_text("Привет! Этот бот своеобразная игра-обучалка по английскому языку. Вы можете выбрать одну"
                              " из тем с помощью команд, которые будут описаны ниже.", reply_markup=markup_start)
    update.message.reply_text("Список команд, которые вы можете использовать: \n/Опрос - бот будет писать вам слово и предлагать выбрать правильный перевод. "
                              "Если допущена ошибка, вам будет предложено выбрать вновь или узнать правильный ответ.\n"
                              "Также присутствует перевод русско-английский и англо-русский. Для этого нужно вызвать команду "
                              "'/Переводчик {текст для перевода}'")
    update.message.reply_text("Переведено сервисом «Яндекс.Переводчик» http://translate.yandex.ru/.")


def stop(bot, update):
    reply_keyboard_stop = [["/start"]]
    update.message.reply_text("Спасибо, что воспользовались ботом. Надеемся вам была полезна работа с ним.", reply_markup=ReplyKeyboardMarkup(reply_keyboard_stop))


def help(bot, update):
    update.message.reply_text("Команды:\n/start - запускает бот заново\n"
                              "/Опрос - начинает опрос. Бот будет писать вам слово и предлагать выбрать правильный перевод."
                              "/stop - завершает опрос."
                              "/Переводчик {текст} - преводит введенный текст")


def quiz(bot, update, user_data):
    user_data["func"] = "quiz"
    choice_word = random.choice(word)
    trans_word = [translater_word(choice_word, "ru-en")]
    while len(trans_word) <= 2:
        w = random.choice(translat)
        if w not in trans_word:
            trans_word.append(w)

    reply_keyboard = [[i for i in trans_word], ["/stop"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    user_data["true_answ"] = choice_word, trans_word[0]
    user_data["keyboard"] = markup

    update.message.reply_text(choice_word, reply_markup=markup)


def answer(bot, update, user_data):
    answ = update.message.text
    if user_data["func"] == "quiz":
        reply_keyboard_true = [["/Опрос"], ["/stop"]]
        reply_keyboard_false = [["Повторить попытку", "Правильный ответ"], ["/stop"]]
        if answ == user_data["true_answ"][1]:
            update.message.reply_text("Правильно!", reply_markup=ReplyKeyboardMarkup(reply_keyboard_true))
        elif answ == "Правильный ответ":
            update.message.reply_text("{}: {}".format(answ, user_data["true_answ"][0]))
        elif answ == "Повторить попытку":
            update.message.reply_text("Вы решили повторить попытку.")
            update.message.reply_text(user_data["true_answ"][0], reply_markup=user_data["keyboard"])
        elif answ != user_data["true_answ"]:
            update.message.reply_text("Не правильно!", reply_markup=ReplyKeyboardMarkup(reply_keyboard_false))
    elif user_data["func"] == "translate":
        text = translater_word(answ, user_data["lang"])
        accompanying_text = "Переведено сервисом «Яндекс.Переводчик» http://translate.yandex.ru/."
        update.message.reply_text("\n\n".join([text, accompanying_text]))



def en_ru(bot, update, user_data):
    update.message.reply_text("Язык перевода: Английский - Русский")
    user_data["lang"] = "en-ru"


def ru_en(bot, update, user_data):
    update.message.reply_text("Язык перевода: Русский - Английский")
    user_data["lang"] = "ru-en"



def translater_word(text, lang):
    translator_uri = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    response = requests.get(
        translator_uri,
        params={
            "key":
            "trnsl.1.1.20180401T224213Z.c1143abeda1b8ddf.366d17dd4a20cb2ccc211c86c4bb1ec637a175de",
            "lang": lang,
            "text": text
        })
    return response.json()["text"][0]


def translater(bot, update, user_data):
    user_data["func"] = "translate"
    reply_keyboard_transl = [["/en_ru", "/ru_en"], ["/Опрос", "/stop"]]
    update.message.reply_text("Вы активировали переводчик.\nВы можете выбрать язык перевода.", reply_markup=ReplyKeyboardMarkup(reply_keyboard_transl))


reply_keyboard_start = [['/Опрос', '/Переводчик'], ["/stop"]]
markup_start = ReplyKeyboardMarkup(reply_keyboard_start, one_time_keyboard=False)

word = ["человек", "стол", "мама", "папа", "сестра"]
translat = [translater_word(i, "ru-en") for i in word]


def main():
    updater = Updater("579972815:AAGbvmvV4Ukoo5wIg19T_9GKVsVW1_e-UnI")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, pass_user_data=True))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("Опрос", quiz, pass_user_data=True))
    dp.add_handler(CommandHandler("en_ru", en_ru, pass_user_data=True))
    dp.add_handler(CommandHandler("ru_en", ru_en, pass_user_data=True))
    dp.add_handler(CommandHandler("Переводчик", translater, pass_user_data=True))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(MessageHandler(Filters.text, answer, pass_user_data=True))

    print("Bot started...")

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
    