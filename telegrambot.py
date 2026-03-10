import logging
import os
import re
import random
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Configurare logging pentru a vedea mesaje în consolă
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Încărcare token din fișierul .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Verificare token
if not TOKEN:
    raise ValueError("Tokenul nu a fost găsit! Asigură-te că fișierul .env există și conține BOT_TOKEN=tokenul_tău")

# Dicționar cu răspunsuri (l-am păstrat exact ca tine, doar am corectat un mic detaliu la "cum aplic?")
response_options = {
    "servicii 🔧⚙": {
        "text": "**🔧 Servicii oferite de CNED:**\n\n"
                "**Audit energetic** - Evaluarea consumului energetic\n"
                "**Proiectare sisteme eficiente** - Soluții personalizate\n"
                "**Consultanță tehnică** - Asistență pentru proiecte EE\n"
                "**Monitorizare consum** - Sisteme de monitorizare\n"
                "**Raportare obligatorii** - Asistență pentru raportări\n\n"
                "*Selectează un serviciu pentru detalii:*",
        "options": ["📊 Audit Energetic", "🏗️ Proiectare", "💼 Consultanță", "📈 Monitorizare", "📑 Raportare", "🏠 Meniul Principal"]
    },
    "📊 audit energetic": {
        "text": "**📊 Audit Energetic**\n\n"
                "*Descriere:* Evaluarea detaliată a consumului energetic al clădirilor, instalațiilor sau proceselor industriale.\n\n"
                "*Beneficii:*\n"
                "• Identificarea punctelor cu pierderi energetice\n"
                "• Recomandări pentru optimizare\n"
                "• Estimarea economiilor potențiale\n"
                "• Pregătire pentru proiecte de modernizare\n\n"
                "*Durata:* 2-4 săptămâni\n",
        "options": ["🏠 Meniul Principal", "Contact📞"]
    },
    "🏗️ proiectare": {
        "text": "**🏗️ Proiectare Sisteme Energetice Eficiente**\n\n"
                "*Servicii incluse:*\n"
                "• Proiectare sisteme fotovoltaice\n"
                "• Proiectare sisteme solare termice\n"
                "• Proiectare pompe de căldură\n"
                "• Proiectare sisteme de izolație termică\n"
                "• Proiectare sisteme de iluminat eficient\n\n"
                "*Documentație necesară:*\n"
                "• Autorizație urbanism\n"
                "• Certificat de proprietate\n"
                "• Situație tehnică actuală",
        "options": ["🏠 Meniul Principal", "Contact📞"]
    },
    "💼 consultanță": {
        "text": "**Oferim consultanță Tehnică și Administrativă**\n\n",
        "options": ["🏠 Meniul Principal", "Contact📞"]
    },
    "📈 monitorizare": {
        "text": "CNED oferă sisteme complete de monitorizare energetică care permit urmărirea continuă a consumului de energie electrică, termică, apă și gaze. Prin intermediul senzorilor non-invazivi instalați în punctele cheie de consum, sistemul colectează date în timp real 24/7, oferind o imagine exactă și actualizată a fluxurilor energetice. \n\n",
        "options": ["🏠 Meniul Principal", "Contact📞"]
    },
    "📑 raportare": {
        "text": "CNED asigură raportarea energetică obligatorie conform Legii 139/2018. Generăm automat rapoarte lunare și anuale cu analiza consumurilor și recomandări de optimizare. Asistăm la raportarea către ANRE și Ministerul Energiei, respectând termenele legale. Beneficii: evitarea amenzilor, acces la fonduri europene, îmbunătățirea imaginii corporative.\n\n",
        "options": ["🏠 Meniul Principal", "Contact📞"]
    },
    "programe de finanțare📝": {
        "text": "Programele noastre disponibile:\n\n"
                "• 1. FEERM\n"
                "• 2. EcoVoucher\n"
                "• 3. Casa Verde\n\n"
                "Alege o opțiune:",
        "options": ["FEERM", "EcoVoucher", "Casa Verde", "Cum aplic?", "🏠 Meniul principal"]
    },
    "contact📞": {
        "text": "📞 **Date de contact:**\n\n"
                "**Telefon:** 022 499 444\n"
                "**Email:** office@cned.gov.md / info@cned.gov.md\n"
                "**Adresa:** Chișinău, str. Albișoara 38, Etajul 4, MD-2005\n\n"
                "Apasă butonul de mai jos pentru a reveni la meniu.",
        "options": ["🏠 Meniul principal"]
    },
    "ℹ️ informații": {
        "text": "ℹ️ **Despre CNED:**\n\n"
                "Centrul Național pentru Energie Durabilă (CNED) este o instituție publică din Republica Moldova aflată în subordinea Ministerului Energiei, menită să coordoneze și să organizeze implementarea politicilor de stat în domeniul eficienței energetice și energiei durabile.",
        "options": ["🎯 Obiective", "📞 Contact", "🏠 Meniul principal"]
    },
    "🎯 obiective": { 
        "text": "**Obiectivele principale ale CNED:**\n\n"
                "✅ Reducem consumul de energie și dependența de energia importată\n\n"
                "✅ Stimulăm investițiile în energie durabilă și tehnologii curate\n\n"
                "✅ Creștem gradul de securitate energetică a țării",
        "options": ["🏠 Meniul principal"]
    },
    "feerm": {
        "text": "**FEERM - Program de eficiență energetică în sectorul rezidențial**\n\n"
                "• Obiectiv: Modernizarea energetică a clădirilor rezidențiale\n"
                "• Beneficiari: Asociațiile de proprietari\n"
                "• Valoarea grantului: până la 70% din costul total\n"
                "• Website: [feerm.cned.gov.md](https://feerm.cned.gov.md/)",
        "options": ["🏠 Meniul principal"]
    },
    "ecovoucher": {
        "text": "**EcoVoucher - Program pentru achiziționarea de electrocasnice eficiente**\n\n"
                "• Obiectiv: Înlocuirea electrocasnicelor vechi cu altele eficiente\n"
                "• Beneficiari: Gospodării casnice\n"
                "• Valoarea voucherului: până la 6000 lei\n"
                "• Website: [old.ecovoucher.md/ro](https://old.ecovoucher.md/ro)",
        "options": ["🏠 Meniul principal"]
    },
    "casa verde": {
        "text": "**Casa Verde - Program pentru instalații solare termice**\n\n"
                "• Obiectiv: Instalarea sistemelor solare pentru încălzirea apei\n"
                "• Beneficiari: Proprietarii de case individuale\n",
        "options": ["🏠 Meniul principal"]
    },
    "cum aplic?": {
        "text": "**Pentru mai multe detalii cu privire la aplicarea pentru unul dintre programele oferite, consultați site-ul oficial: https://cned.gov.md/ro**\n\n",
        "options": ["🏠 Meniul principal"]   # am adăugat opțiunea de revenire
    }
}

# Funcția de start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "Salut! Sunt asistentul tău CNED! 💡\n\n"
    welcome_text += "Pot să-ți ofer informații despre:\n"
    welcome_text += "• Servicii 🔧⚙\n• Programe de finanțare📝\n• Contact📞\n• Informațiiℹ️"
    
    keyboard = [
        ["Servicii 🔧⚙", "Programe de finanțare📝"],
        ["Contact📞", "ℹ️ Informații"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Funcție pentru a răspunde mesajelor
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Dacă utilizatorul scrie "meniul principal" sau apasă butonul corespunzător
    if "meniul principal" in user_message.lower() or "🏠" in user_message:
        await start(update, context)
        return
    
    # Normalizăm mesajul pentru căutare (eliminăm emoji-urile și facem lowercase)
    normalized_message = user_message.lower()
    search_message = re.sub(r'[^\w\s]', '', normalized_message).strip()
    
    # Căutăm cel mai potrivit răspuns
    response = None
    matched_key = None
    
    # Mai întâi încercăm să găsim o potrivire exactă
    for key in response_options:
        normalized_key = re.sub(r'[^\w\s]', '', key.lower()).strip()
        if search_message == normalized_key or normalized_message == key.lower():
            response = response_options[key]
            matched_key = key
            break
    
    # Dacă nu găsim potrivire exactă, căutăm parțial
    if not response:
        for key in response_options:
            normalized_key = re.sub(r'[^\w\s]', '', key.lower()).strip()
            if normalized_key in search_message or search_message in normalized_key:
                response = response_options[key]
                matched_key = key
                break
    
    # Dacă nu găsim un răspuns specific, oferim răspuns generic
    if not response:
        random_responses = [
            "Nu sunt sigur că înțeleg. Pot să te ajut cu alte informații?",
            "Vrei să începem cu meniul principal pentru a vedea toate opțiunile?"
        ]
        generic_text = random.choice(random_responses)
        keyboard = [
            ["Servicii 🔧⚙", "Programe de finanțare📝"],
            ["Contact📞", "ℹ️ Informații"],
            ["🏠 Meniul principal"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(generic_text, reply_markup=reply_markup)
        return
    
    # Verificăm dacă răspunsul are opțiuni pentru tastatură
    if "options" in response:
        # Creăm tastatura cu opțiunile pentru răspuns
        keyboard = []
        options = response["options"]
        
        # Grupăm opțiunile câte 2 pe rând
        for i in range(0, len(options), 2):
            if i + 1 < len(options):
                keyboard.append([options[i], options[i + 1]])
            else:
                keyboard.append([options[i]])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(response["text"], reply_markup=reply_markup, parse_mode='Markdown')
    else:
        # Dacă nu are opțiuni, trimitem doar textul cu buton pentru meniul principal
        keyboard = [["🏠 Meniul principal"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(response["text"], reply_markup=reply_markup, parse_mode='Markdown')

# Funcție pentru comanda /custom
async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = (
        "🤖 **CNEDBot - Asistentul tău virtual**\n\n"
        "**Comenzi disponibile:**\n"
        "/start - Începe conversația\n"
        "/custom - Informații despre bot\n"
        "/help - Ajutor\n\n"
        "**Interacțiune:**\n"
        "Folosește butoanele pentru a naviga prin meniuri!"
    )
    await update.message.reply_text(info_text, parse_mode='Markdown')

# Funcție pentru comanda /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🆘 **Ajutor**\n\n"
        "1. Apasă butoanele pentru a naviga\n"
        "2. Scrie cuvinte cheie\n"
        "3. Folosește 'Meniul principal' pentru a reveni\n\n"
        "💡 **Sugestii:**\n"
        "• Încearcă să scrii 'Contact' sau 'Informații'\n"
        "• Explorează toate categoriile\n"
        "• Botul îți va oferi opțiuni pentru a continua"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Construirea aplicației și adăugarea handler-elor
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('custom', custom))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 Botul rulează... (apasă Ctrl+C pentru a opri)")
    application.run_polling()

if __name__ == "__main__":
    main()