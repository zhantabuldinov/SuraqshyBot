from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters, CallbackQueryHandler
import google.generativeai as genai
import random

TOKEN = "YOUR_TOKEN"
GEMINI_API_KEY = "YOUR_API"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

#  ПРЕСЕТЫ 
WORDS = {
    "сенім": "Сенім — бұл адамға немесе іске деген ішкі сену сезімі.\nМысал: Мен досыма сенім артамын.",
    "мәдениет": "Мәдениет — халықтың дәстүрі, тілі, өнері және өмір салты.",
    "құндылық": "Құндылық — адам үшін маңызды нәрсе.\nМысал: Отбасы — басты құндылық.",
    "жауапкершілік": "Жауапкершілік — өз іс-әрекетіне жауап беру.",
    "білім": "Білім — оқу арқылы алынатын ақпарат пен тәжірибе."
}

#  ЦИФРОВОЙ КОНСУЛЬТАНТ
SECURITY_TIPS = {
    "пароль": "🔐 Құпия сөздің ережелері:\n• Кем дегенде 12 символ\n• Әр түрлі сандар, әріптер, белгілер қолданыңыз\n• Құпиясөзді ұмытпай, басқалар арасында бөліспеңіз\n• Қазір құпиясөз жеңіл болса, өзгертіңіз.",
    "фейк": "⚠️ Фейк ақпаратқа алданбау үшін:\n• Ақпараттың дереккөзін тексеріңіз (ресми сайт па, сенімді медиа ма).\n• Бір жаңалықты бірнеше жерден салыстырып көріңіз.\n• Өте эмоциялық немесе қорқынышты тақырыптарға бірден сенбеңіз.\n• Күмәнді сілтемелерді ашпаңыз және тексерілмеген ақпаратты таратпаңыз.",
    "интернет": "🌐 Интернеттің қауіпсіздігі:\n• VPN арқылы ашық Wi-Fi ұйымдарында қосылмаңыз\n• Сенімсіз сайттаға кірмеңіз\n• Кез-келген файлды орнату үшін алдымен оны тексеріңіз\n• Антивирус бағдарламасын өзінің компьютерінде орнатыңыз"
}

#  КУЛЬТУРНЫЙ НАВИГАТОР
CULTURAL_PLACES = {
    "театр": "🎭 Казахстанның театрлары:\n• Абай атындағы Ұлттық опера және балет театры\n• Қазақ драма театры\n• Астана Опера театры\n👉 Ішінен іздеңіз: https://ticketon.kz/astana/theatres",
    "кино": "🎬 Қазақша кинотеатрлар:\n• Imax Almaty\n• Евразия кинотеатры\n• Казахстан кинотеатры\n📍 Афиша: https://ticketon.kz/astana/cinema",
    "мероприятие": "🎉 Мәдени іс-шараларының атласы:\n• Этнофестивали\n• Ғалым конференциялары\n• Музыкалық фестивальдар\n📌 Іздеу: https://ticketon.kz/"
}

#  ЯЗЫКОВОЙ АССИСТЕНТ
LANGUAGE_EXAMPLES = {
    "орфография": "✏️ Орфография тексті тексте:\n• 'Қабылданыңыз' емес 'Қабылдаңыз'\n• 'Келдіміңіз' емес 'Келдіңіз бе?'\n• 'Білім берілу' емес 'Білім беру'\n💡 Сөздіктерді тексеріңіз: https://sozdik.kz/",
    "перевод": "🌍 Әрқайсысының аудармасы:\n• Цифрлық - Digital\n• Қауіпсіздік - Security\n• Мәдениет - Culture\n📚 Практика: https://translate.yandex.ru/dictionary/%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-%D0%90%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9/%D0%9A%D0%B0%D0%B7%D0%B0%D1%85%D1%81%D0%BA%D0%B8%D0%B9",
    "грамматика": "📖 Қазақ грамматика ережелері:\n• Сөз түзілісі (синтаксис)\n• Әріп құрылымы (морфология)\n• Дыбыстық ережелер\n🎓 Қазақшаны тез үйрену: https://soyle.kz/"
}

#  МОТИВИРУЮЩИЕ ВЫСКАЗЫВАНИЯ
MOTIVATIONS = [
    "✨ Бүгін жасаған әрбір ісіңіз – алға жасалған қадам. Өзіңізбен мақтаныңыз! 💪",
    "🌟 Сіз көп нәрсеге қабілетті жансыз. Мақсатыңызға сеніммен қадам басыңыз! 🚀",
    "💎 Қателіктер – өсуге берілген мүмкіндік. Әр тәжірибе сізді күштірек етеді! 🎯",
    "🌈 Сіз бірегей адамсыз. Өз жолыңызбен батыл жүріңіз! ✨",
    "🔥 Барлығы өз қолыңызда. Әлеуетіңіз шексіз екенін ұмытпаңыз! 💯",
    "🎨 Әр күн – жаңа мүмкіндік. Бүгінгі күнді пайдалы өткізіңіз! 🌺",
    "🌙 Демалыс та маңызды. Өзіңізге уақыт бөліп, күш жинауды ұмытпаңыз! 🧘",
    "⭐ Сіз көп нәрсеге қол жеткізе аласыз. Өзіңізге деген сенімді сақтаңыз! 🌟",
    "💪 Әрбір сынақ сізді мықты етеді. Берілмей, алға жылжи беріңіз! 🎖️",
    "🏆 Табыс – үздіксіз еңбектің нәтижесі. Кішкентай қадамдар да үлкен жетістікке апарады! 🎪",
    "🌸 Жақсы ойлар мен жақсы істер өмірді әдемі етеді. Позитивті болыңыз! 💝",
    "🎯 Мақсатыңыз айқын болса, жол да табылады. Армандарыңыздан бас тартпаңыз! 🚀",
    "🌊 Қиындықтар уақытша. Сабыр сақтап, өзіңізге сеніңіз! 🌟",
    "🎁 Әр күн – жаңа мүмкіндік. Бүгін бір жақсы іс жасауға тырысыңыз! ✨",
    "🦋 Өзгерістерден қорықпаңыз. Олар сізді жаңа деңгейге шығарады! 💖",
    "🔮 Болашағыңыз өз қолыңызда. Бүгіннен бастап әрекет етіңіз! 🚀",
    "🎪 Әр сәтті бағалай біліңіз. Кішкентай қуаныштардың өзі үлкен күш береді! 🎯",
    "💝 Жақсылық жасаған сайын өміріңіз де жарық бола түседі. Жақсылықтан жалықпаңыз! ⭐",
    "🌟 Сіз ойлағаннан да мықтысыз. Барлығын еңсере алатыныңызға сеніңіз! 💫",
    "🔆 Жақындарыңыз сізге сенеді. Сол сенімді ақтауға тырысыңыз! 🌈",
    "💘 Жылы сөз бен мейірім әрдайым маңызды. Айналаңызға жақсы энергия сыйлаңыз! 🎨"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 Сөздік", callback_data="words")],
        [InlineKeyboardButton("🔒 Цифрлық консультант", callback_data="security")],
        [InlineKeyboardButton("🎭 Мәдени навигатор", callback_data="culture")],
        [InlineKeyboardButton("📖 Тіл ассистенті", callback_data="language")],
        [InlineKeyboardButton("🍪 Күнінің мотивациясы", callback_data="motivation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Suraqshy — сенімді қазақша көмекші 🤖\n\n"
        "Келесіні таңдаңыз:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text.lower().strip()
    if word in WORDS:
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(WORDS[word], reply_markup=reply_markup)
    elif word in SECURITY_TIPS:
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="security")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(SECURITY_TIPS[word], reply_markup=reply_markup)
    elif word in CULTURAL_PLACES:
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="culture")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(CULTURAL_PLACES[word], reply_markup=reply_markup)
    elif word in LANGUAGE_EXAMPLES:
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="language")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(LANGUAGE_EXAMPLES[word], reply_markup=reply_markup)
    else:
        if any(ord(c) >= 0x0400 for c in word):
            await update.message.reply_text("⏳ Іздеп жатырмын... Бірсәт күтіңіз")
            
            try:
                prompt = f"""Объясни казахское слово '{word}' на казахском языке. 
Дай краткое, четкое объяснение (2-3 предложения).
Если возможно, добавь пример использования.
Формат ответа:
[СЛОВО] — [Объяснение]
Пример: [Пример использования]"""
                
                response = model.generate_content(prompt)
                explanation = response.text
                
                WORDS[word] = explanation
                
                keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="back_to_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"✨ Жаңа сөз табылды!\n\n{explanation}",
                    reply_markup=reply_markup
                )
            except Exception as e:
                await update.message.reply_text(
                    f"⚠️ Қате болды: {str(e)}\n\n"
                    "Іздеуді қайта көріңіз немесе басқа сөз жазыңыз."
                )
        else:
            await update.message.reply_text(
                "Бұл сөз сөздікте жоқ 🤔\n\n"
                "Бот мынадай команды білетін болып төмендегілерін пайдаланыңыз:\n"
                "/start — басты меню\n"
                "/security — цифрлық қауіпсіздік\n"
                "/culture — мәдени навигатор\n"
                "/language — тіл ассистенті"
            )

#  ЦИФРОВОЙ КОНСУЛЬТАНТ
async def security_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Пароль", callback_data="sec_password")],
        [InlineKeyboardButton("⚠️ Фейк ақпарат", callback_data="sec_fake")],
        [InlineKeyboardButton("🌐 Интернеттің қауіпсіздігі", callback_data="sec_internet")],
        [InlineKeyboardButton("⬅️ Артқа", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔒 Цифрлық консультант - қауіпсіздік кеңеслері\n\n"
        "Тақырыпты таңдаңыз:",
        reply_markup=reply_markup
    )

async def handle_security(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.lower()
    if topic in SECURITY_TIPS:
        await update.message.reply_text(SECURITY_TIPS[topic])

#  КУЛЬТУРНЫЙ НАВИГАТОР
async def cultural_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎭 Театрлар", callback_data="cult_theatre")],
        [InlineKeyboardButton("🎬 Кинотеатрлар", callback_data="cult_cinema")],
        [InlineKeyboardButton("🎉 Мероприятия", callback_data="cult_events")],
        [InlineKeyboardButton("⬅️ Артқа", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎭 Мәдени навигатор - қайда барсақ болады?\n\n"
        "Сіздің қызығушылығын таңдаңыз:",
        reply_markup=reply_markup
    )

async def handle_culture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = update.message.text.lower()
    if place in CULTURAL_PLACES:
        await update.message.reply_text(CULTURAL_PLACES[place])

#  ЯЗЫКОВОЙ АССИСТЕНТ
async def language_assistant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✏️ Орфография", callback_data="lang_ortho")],
        [InlineKeyboardButton("🌍 Перевод", callback_data="lang_translate")],
        [InlineKeyboardButton("📖 Грамматика", callback_data="lang_grammar")],
        [InlineKeyboardButton("⬅️ Артқа", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📚 Тіл ассистенті - тіл ережелері және аудармасы\n\n"
        "Тақырыпты таңдаңыз:",
        reply_markup=reply_markup
    )

async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.lower()
    if topic in LANGUAGE_EXAMPLES:
        await update.message.reply_text(LANGUAGE_EXAMPLES[topic])

#  ОБРАБОТЧИК КНОПОК
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Главное меню
    if query.data == "words":
        keyboard = [
            [InlineKeyboardButton("сенім", callback_data="word_senіm"),
             InlineKeyboardButton("мәдениет", callback_data="word_madeniet")],
            [InlineKeyboardButton("құндылық", callback_data="word_qundylyq"),
             InlineKeyboardButton("жауапкершілік", callback_data="word_jauapkershilіk")],
            [InlineKeyboardButton("білім", callback_data="word_bilіm")],
            [InlineKeyboardButton("⬅️ Артқа", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📚 Қазақша терминдер сөздігі\n\n"
            "Сөз таңдаңыз:",
            reply_markup=reply_markup
        )
    
    # СЛОВАРЬ 
    elif query.data == "word_senіm":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="words")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            WORDS["сенім"],
            reply_markup=reply_markup
        )
    elif query.data == "word_madeniet":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="words")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            WORDS["мәдениет"],
            reply_markup=reply_markup
        )
    elif query.data == "word_qundylyq":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="words")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            WORDS["құндылық"],
            reply_markup=reply_markup
        )
    elif query.data == "word_jauapkershilіk":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="words")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            WORDS["жауапкершілік"],
            reply_markup=reply_markup
        )
    elif query.data == "word_bilіm":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="words")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            WORDS["білім"],
            reply_markup=reply_markup
        )
    
    # SECURITY
    elif query.data == "security":
        keyboard = [
            [InlineKeyboardButton("🔐 Пароль", callback_data="sec_password")],
            [InlineKeyboardButton("⚠️ Фейк ақпарат", callback_data="sec_fake")],
            [InlineKeyboardButton("🌐 Интернет қауіпсіздігі", callback_data="sec_internet")],
            [InlineKeyboardButton("⬅️ Артқа", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔒 Цифрлық консультант - қауіпсіздік кеңеслері\n\n"
            "Тақырыпты таңдаңыз:",
            reply_markup=reply_markup
        )
    
    elif query.data == "sec_password":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="security")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            SECURITY_TIPS["пароль"],
            reply_markup=reply_markup
        )
    elif query.data == "sec_fake":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="security")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            SECURITY_TIPS["фейк"],
            reply_markup=reply_markup
        )
    elif query.data == "sec_internet":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="security")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            SECURITY_TIPS["интернет"],
            reply_markup=reply_markup
        )
    
    # CULTURE
    elif query.data == "culture":
        keyboard = [
            [InlineKeyboardButton("🎭 Театрлар", callback_data="cult_theatre")],
            [InlineKeyboardButton("🎬 Кинотеатрлар", callback_data="cult_cinema")],
            [InlineKeyboardButton("🎉 Мероприятия", callback_data="cult_events")],
            [InlineKeyboardButton("⬅️ Артқа", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎭 Мәдени навигатор - қайда барсақ болады?\n\n"
            "Сіздің қызығушылығын таңдаңыз:",
            reply_markup=reply_markup
        )
    
    elif query.data == "cult_theatre":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="culture")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            CULTURAL_PLACES["театр"],
            reply_markup=reply_markup
        )
    elif query.data == "cult_cinema":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="culture")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            CULTURAL_PLACES["кино"],
            reply_markup=reply_markup
        )
    elif query.data == "cult_events":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="culture")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            CULTURAL_PLACES["мероприятие"],
            reply_markup=reply_markup
        )
    
    # LANGUAGE
    elif query.data == "language":
        keyboard = [
            [InlineKeyboardButton("✏️ Орфография", callback_data="lang_ortho")],
            [InlineKeyboardButton("🌍 Перевод", callback_data="lang_translate")],
            [InlineKeyboardButton("📖 Грамматика", callback_data="lang_grammar")],
            [InlineKeyboardButton("⬅️ Артқа", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📚 Тіл ассистенті - тіл ережелері және аудармасы\n\n"
            "Тақырыпты таңдаңыз:",
            reply_markup=reply_markup
        )
    
    elif query.data == "lang_ortho":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="language")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            LANGUAGE_EXAMPLES["орфография"],
            reply_markup=reply_markup
        )
    elif query.data == "lang_translate":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="language")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            LANGUAGE_EXAMPLES["перевод"],
            reply_markup=reply_markup
        )
    elif query.data == "lang_grammar":
        keyboard = [[InlineKeyboardButton("⬅️ Артқа", callback_data="language")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            LANGUAGE_EXAMPLES["грамматика"],
            reply_markup=reply_markup
        )
    
    # MOTIVATION
    elif query.data == "motivation":
        motivation_text = random.choice(MOTIVATIONS)
        keyboard = [
            [InlineKeyboardButton("🔄 Басқа мотивация", callback_data="motivation")],
            [InlineKeyboardButton("⬅️ Артқа", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🍪 Күнінің мотивациясы:\n\n{motivation_text}",
            reply_markup=reply_markup
        )
    
    # BACK TO MAIN MENU
    elif query.data == "back_to_menu":
        keyboard = [
            [InlineKeyboardButton("📚 Сөздік", callback_data="words")],
            [InlineKeyboardButton("🔒 Цифрлық консультант", callback_data="security")],
            [InlineKeyboardButton("🎭 Мәдени навигатор", callback_data="culture")],
            [InlineKeyboardButton("📖 Тіл ассистенті", callback_data="language")],
            [InlineKeyboardButton("🍪 Күнінің мотивациясы", callback_data="motivation")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Suraqshy — сенімді қазақша көмекші 🤖\n\n"
            "Келесіні таңдаңыз:",
            reply_markup=reply_markup
        )

app = ApplicationBuilder().token(TOKEN).build()

# Команда /start
app.add_handler(CommandHandler("start", start))

# Новые команды
app.add_handler(CommandHandler("security", security_tips))
app.add_handler(CommandHandler("culture", cultural_guide))
app.add_handler(CommandHandler("language", language_assistant))

# Обработчик кнопок (CallbackQuery)
app.add_handler(CallbackQueryHandler(button_handler))

# Обычные текстовые сообщения
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    app.run_polling()
