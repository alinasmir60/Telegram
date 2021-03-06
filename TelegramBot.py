from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from telegram import ReplyKeyboardMarkup
import requests
import random

file = open("word.txt", encoding="utf-8")
string = file.read()
file.close()

file = open("irregular_verbs.txt", encoding="utf-8")
verbs = file.readlines()
file.close()


def start(bot, update, user_data):
    user_data["lang"] = lang_ru
    update.message.reply_text("Привет! Этот бот своеобразная игра-обучалка по английскому языку. Вы можете выбрать одну"
                              " из тем с помощью команд, которые будут описаны ниже.", reply_markup=markup_start)
    update.message.reply_text("Список команд, которые вы можете использовать: "
                              "\n1) /quiz - бот будет писать вам слово и предлагать выбрать правильный перевод. "
                              "Если допущена ошибка, вам будет предложено выбрать вновь или узнать правильный ответ."
                              "\n2) /irr_verbs - это тест на знание неправильных глаголов. "
                              "Бот называет глагол, а вы должны выбрать правильное написание"
                              "\n\nТакже присутствует перевод русско-английский и англо-русский. "
                              "Для этого нужно вызвать команду /translater. Изначально Переводчик настроен на "
                              "русско-английский перевод, но вы можете самостоятельно изменить направление с "
                              "помощью команд /en_ru (англо-русский) и /ru_en (русско-английский)")
    update.message.reply_text("Переведено сервисом «Яндекс.Переводчик» http://translate.yandex.ru/.")


def stop(bot, update):
    reply_keyboard_stop = [["/start"]]
    update.message.reply_text("Спасибо, что воспользовались ботом. Надеемся вам была полезна работа с ним.",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard_stop))


def help(bot, update):
    update.message.reply_text('''
    Команды:
    /start - запускает бот;
    /quiz - начинает опрос по словам;
    /irr_verbs - тест по неправильным глаголам;
    /translater - преводит введенный текст;
    /ru_en - меняет направление перевода на русско-английский;
    /en_ru - меняет направление перевода на англо-русский; 
    /stop - завершает работу бота.''')


def quiz(bot, update, user_data):
    user_data["func"] = "quiz"
    choice_word, trans_word = choose_word(user_data["func"])

    reply_keyboard = [[i for i in trans_word], ["/stop"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    user_data["true_answ"] = choice_word, trans_word[0]
    user_data["false_answ"] = trans_word[1:]
    user_data["keyboard"] = markup

    update.message.reply_text(choice_word, reply_markup=markup)


def irregular_verbs(bot, update, user_data):
    update.message.reply_text("Вы выбрали тест по неправильным глаголам")
    user_data["func"] = "verbs"

    choice_word, trans_word = choose_word(user_data["func"])

    reply_keyboard = [[i for i in trans_word], ["/stop"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    user_data["true_answ"] = choice_word, trans_word[1]
    user_data["false_answ"] = trans_word[0]
    user_data["keyboard"] = markup

    update.message.reply_text(choice_word, reply_markup=markup)


def translater(bot, update, user_data):
    user_data["func"] = "translate"

    # клавиатура для переводчика
    reply_keyboard_transl = [["/en_ru", "/ru_en"], ["/irr_verbs", "/quiz", "/stop"]]

    update.message.reply_text("Вы активировали переводчик.\nВы можете выбрать язык перевода.",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard_transl))


def answer(bot, update, user_data):
    answ = update.message.text.lower()

    # клавиатура при правильном ответе
    reply_keyboard_true = [["/quiz", "/irr_verbs"], ["/translater", "/stop"]]

    # клавиатура при неправильном ответе
    reply_keyboard_false = [["Повторить попытку", "Правильный ответ"], ["/quiz", "/irr_verbs", "/translater", "/stop"]]

    markup = user_data["keyboard"]

    if user_data["func"] == "quiz" or user_data["func"] == "verbs":
        if answ == user_data["true_answ"][1]:
            user_data["answer"] = "true"
            update.message.reply_text("правильно!", reply_markup=ReplyKeyboardMarkup(reply_keyboard_true))
        elif answ == "правильный ответ":
            user_data["answer"] = "true"
            update.message.reply_text("{}: {}".format(answ, user_data["true_answ"][1]),
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard_true))
        elif answ == "повторить попытку":
            user_data["answer"] = "retry"
            update.message.reply_text("Вы решили повторить попытку.")
            update.message.reply_text(user_data["true_answ"][0], reply_markup=user_data["keyboard"])
        elif answ != user_data["true_answ"] and answ in user_data["false_answ"]:
            user_data["answer"] = "false"
            update.message.reply_text("Не правильно!", reply_markup=ReplyKeyboardMarkup(reply_keyboard_false))
        else:
            if user_data["answer"] == "retry":
                markup = user_data["keyboard"]
            elif user_data["answer"] == "true":
                markup = ReplyKeyboardMarkup(reply_keyboard_true)
            elif user_data["answer"] == "false":
                markup = ReplyKeyboardMarkup(reply_keyboard_false)
            update.message.reply_text("Извините, произошла ошибка при обработке Вашего ответа."
                                      "\nВы можете выбрать слово/команду на клавиатуре бота(если она скрыта, то нажмите"
                                      " на значок) или ввести слово на клавиатуре(!если этого слова не будет на "
                                      "клавиатуре, то вы вновь увидите это сообщение, поэтому лучше воспользоваться "
                                      "клавиатурой!)",
                                      reply_markup=markup)
    elif user_data["func"] == "translate":
        text = translater_word(answ, user_data["lang"])
        accompanying_text = "Переведено сервисом «Яндекс.Переводчик» http://translate.yandex.ru/."
        update.message.reply_text("\n\n".join([text, accompanying_text]))
    else:
        update.message.reply_text("Упс... Произошла ошибка при обработке вашего запроса. Пожалуйста выберите нужную "
                                  "команду на клавиатуре", reply_markup=ReplyKeyboardMarkup(reply_keyboard_start))


def en_ru(bot, update, user_data):
    if user_data["func"] == "translate":
        update.message.reply_text("Язык перевода: Английский - Русский")
        user_data["lang"] = lang_en
    else:
        update.message.reply_text("Вызов данной команды возможен только после вызова команды /translater.")


def ru_en(bot, update, user_data):
    if user_data["func"] == "translate":
        update.message.reply_text("Язык перевода: Русский - Английский")
        user_data["lang"] = lang_ru
    else:
        update.message.reply_text("Вызов данной команды возможен только после вызова команды /translater.")


def choose_word(func):
    if func == "quiz":
        choice_word = random.choice(word)
        trans_word = [translater_word(choice_word, lang_ru)]
        while len(trans_word) <= 2:
            w = random.choice(translat)
            if w not in trans_word:
                trans_word.append(w)
        return choice_word, trans_word
    elif func == "verbs":
        choice_word = random.choice(list(irr_verbs.keys()))
        trans_word = [irr_verbs[choice_word], translater_word(choice_word, lang_ru)]
        return choice_word, trans_word


def translater_word(text, lang):
    translator_uri = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    response = requests.get(
        translator_uri,
        params={
            "key": "trnsl.1.1.20180401T224213Z.c1143abeda1b8ddf.366d17dd4a20cb2ccc211c86c4bb1ec637a175de",
            "lang": lang,
            "text": text
        })
    return response.json()["text"][0]


lang_ru = "ru-en"
lang_en = "en-ru"

word = string.split(", ")
translat = [translater_word(i, lang_ru) for i in word]

irr_verbs = {}
for i in verbs:
    str_i = i.split()
    irr_verbs[str_i[1]] = str_i[0]

reply_keyboard_start = [["/quiz", "/irr_verbs", "/translater"], ["/stop"]] #стандартная клавиатура
markup_start = ReplyKeyboardMarkup(reply_keyboard_start, one_time_keyboard=False)


def main():
    updater = Updater("579972815:AAGbvmvV4Ukoo5wIg19T_9GKVsVW1_e-UnI")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, pass_user_data=True))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("quiz", quiz, pass_user_data=True))
    dp.add_handler(CommandHandler("translater", translater, pass_user_data=True))
    dp.add_handler(CommandHandler("en_ru", en_ru, pass_user_data=True))
    dp.add_handler(CommandHandler("ru_en", ru_en, pass_user_data=True))
    dp.add_handler(CommandHandler("irr_verbs", irregular_verbs, pass_user_data=True))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(MessageHandler(Filters.text, answer, pass_user_data=True))

    print("Bot started...")

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
