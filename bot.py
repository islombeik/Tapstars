import asyncio
import sqlite3
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

API_TOKEN = "9024406358:AAGKtZAbhfHCrMMgTC2Zh5gswThDbGMYk4M"
WEBAPP_URL = "https://islombeik.github.io/Tapstars/
ADMIN_ID = 8444733475  # O'zingizning Telegram ID raqamingiz

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Ma'lumotlar bazasi (SQLite)
conn = sqlite3.connect("stars_game_v2.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    lang TEXT DEFAULT 'uz',
    is_paid INTEGER DEFAULT 0,
    coins INTEGER DEFAULT 0,
    multitap INTEGER DEFAULT 1,
    energy_limit INTEGER DEFAULT 1000,
    referrer_id INTEGER DEFAULT 0,
    referrals_count INTEGER DEFAULT 0
)
""")
conn.commit()

# 3 ta til uchun barcha matnlar lug'ati
TEXTS = {
    "uz": {
        "welcome_pay": "🚀 **STARS 2X TAP** o'yiniga xush kelibsiz!\n\n💎 Qoidalar:\n• Kirish narxi: **50 Stars** (bir martalik)\n• Maqsad: **1 000 000** tanga yig'ish\n• Mukofot: **100 Stars**!\n• Har bir do'st uchun: **+50 000 tanga**\n\nBoshlash uchun chiptani faollashtiring 👇",
        "btn_pay": "⭐️ O'yinga kirish (50 Stars)",
        "cabinet": "⭐️ **Shaxsiy kabinet:**\n🪙 Tangalar: **{coins:,}**\n⚡ Bosish kuchi: **+{tap}**\n👥 Do'stlar: **{refs} ta**\n\nO'ynash uchun tugmani bosing 👇",
        "btn_play": "🎮 O'YINNI BOSHLASH (TAP)",
        "btn_boost": "⚡ 2X Kuchaytirgich (25 Stars)",
        "btn_ref": "👥 Do'st chaqirish (+50 000 🪙)",
        "btn_claim": "🎁 1 000 000 tangani 100 Starsga almashtirish",
        "btn_lang": "🌐 Tilni o'zgartirish",
        "paid_ok": "✅ Tabriklaymiz! O'yin ochildi!",
        "boost_ok": "⚡ **2X BOOST FAOLLASHTIRILDI!** Endi har bir bosishda 2 barobar ko'p tanga olasiz!",
        "ref_bonus": "🎉 Siz taklif qilgan do'stingiz o'yinga qo'shildi! Hisobingizga **+50 000 tanga** qo'shildi!",
        "ref_text": "👥 **Do'stlarni chaqiring va tanga ishlang!**\n\nQuyidagi havolani do'stlaringizga yuboring. Do'stingiz kirish chiptasini (50 Stars) faollashtirishi bilan sizga **50 000 tanga** beriladi!\n\n🔗 Sizning havolangiz:\n`{link}`",
        "not_enough": "❌ Sizda {coins:,} tanga bor. Kamida 1 000 000 kerak!",
        "claim_ok": "🎉 **TABRIKLAYMIZ!** 1 000 000 tanga almashtirildi! 100 Stars mukofotingiz tez orada yuboriladi."
    },
    "en": {
        "welcome_pay": "🚀 Welcome to **STARS 2X TAP**!\n\n💎 Rules:\n• Entry fee: **50 Stars** (one-time)\n• Goal: Collect **1,000,000** coins\n• Reward: **100 Stars**!\n• Per invited friend: **+50,000 coins**\n\nActivate your entry pass to start 👇",
        "btn_pay": "⭐️ Enter Game (50 Stars)",
        "cabinet": "⭐️ **Dashboard:**\n🪙 Coins: **{coins:,}**\n⚡ Tap Power: **+{tap}**\n👥 Friends: **{refs}**\n\nPress the button below to play 👇",
        "btn_play": "🎮 START GAME (TAP)",
        "btn_boost": "⚡ 2X Multitap Boost (25 Stars)",
        "btn_ref": "👥 Invite Friends (+50,000 🪙)",
        "btn_claim": "🎁 Exchange 1,000,000 coins for 100 Stars",
        "btn_lang": "🌐 Change Language",
        "paid_ok": "✅ Congratulations! The game is unlocked!",
        "boost_ok": "⚡ **2X BOOST ACTIVATED!** You now earn double coins per tap!",
        "ref_bonus": "🎉 Your invited friend joined the game! **+50,000 coins** added to your balance!",
        "ref_text": "👥 **Invite Friends & Earn Coins!**\n\nShare your link below. Once your friend activates their entry pass (50 Stars), you instantly get **50,000 coins**!\n\n🔗 Your link:\n`{link}`",
        "not_enough": "❌ You have {coins:,} coins. You need at least 1,000,000!",
        "claim_ok": "🎉 **CONGRATULATIONS!** 1,000,000 coins exchanged! Your 100 Stars reward is on the way."
    },
    "ru": {
        "welcome_pay": "🚀 Добро пожаловать в **STARS 2X TAP**!\n\n💎 Правила:\n• Вход: **50 Stars** (единоразово)\n• Цель: Собрать **1 000 000** монет\n• Награда: **100 Stars**!\n• За каждого друга: **+50 000 монет**\n\nАктивируйте билет, чтобы начать 👇",
        "btn_pay": "⭐️ Войти в игру (50 Stars)",
        "cabinet": "⭐️ **Личный кабинет:**\n🪙 Монеты: **{coins:,}**\n⚡ Сила клика: **+{tap}**\n👥 Друзья: **{refs}**\n\nНажмите кнопку ниже, чтобы играть 👇",
        "btn_play": "🎮 НАЧАТЬ ИГРУ (TAP)",
        "btn_boost": "⚡ 2X Усилитель (25 Stars)",
        "btn_ref": "👥 Пригласить друга (+50 000 🪙)",
        "btn_claim": "🎁 Обменять 1 000 000 монет на 100 Stars",
        "btn_lang": "🌐 Сменить язык",
        "paid_ok": "✅ Поздравляем! Игра открыта!",
        "boost_ok": "⚡ **2X БУСТ АКТИВИРОВАН!** Теперь вы получаете в 2 раза больше монет за клик!",
        "ref_bonus": "🎉 Ваш приглашенный друг вошел в игру! Вам начислено **+50 000 монет**!",
        "ref_text": "👥 **Приглашайте друзей и получайте монеты!**\n\nОтправьте ссылку друзьям. Как только друг активирует вход (50 Stars), вы получите **50 000 монет**!\n\n🔗 Ваша ссылка:\n`{link}`",
        "not_enough": "❌ У вас {coins:,} монет. Нужно минимум 1 000 000!",
        "claim_ok": "🎉 **ПОЗДРАВЛЯЕМ!** 1 000 000 монет обменяны! Награда 100 Stars скоро будет отправлена."
    }
}

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="setlang_uz"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru")
        ]
    ])

# /start va referral ID ni ushlash
@dp.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    user = get_user(user_id)

    if not user:
        ref_id = 0
        if command.args and command.args.isdigit():
            potential_ref = int(command.args)
            if potential_ref != user_id and get_user(potential_ref):
                ref_id = potential_ref
        cursor.execute("INSERT INTO users (user_id, referrer_id) VALUES (?, ?)", (user_id, ref_id))
        conn.commit()
        await message.answer("🌐 Tilni tanlang / Choose language / Выберите язык:", reply_markup=lang_keyboard())
    else:
        await show_main(message, user_id)

# Tilni saqlash
@dp.callback_query(F.data.startswith("setlang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    cursor.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    await callback.message.delete()
    await show_main(callback.message, user_id)

@dp.callback_query(F.data == "change_lang")
async def change_lang_menu(callback: types.CallbackQuery):
    await callback.message.answer("🌐 Tilni tanlang / Choose language / Выберите язык:", reply_markup=lang_keyboard())
    await callback.answer()

async def show_main(message: types.Message, user_id: int):
    user = get_user(user_id)
    lang, is_paid, coins, tap, energy, ref_id, refs_count = user[1], user[2], user[3], user[4], user[5], user[6], user[7]
    t = TEXTS[lang]

    if is_paid == 0:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t["btn_pay"], callback_data="pay_entry")],
            [InlineKeyboardButton(text=t["btn_lang"], callback_data="change_lang")]
        ])
        await message.answer(t["welcome_pay"], reply_markup=kb, parse_mode="Markdown")
    else:
        url = f"{WEBAPP_URL}?coins={coins}&tap={tap}&energy={energy}&lang={lang}"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t["btn_play"], web_app=WebAppInfo(url=url))],
            [InlineKeyboardButton(text=t["btn_boost"], callback_data="buy_boost")],
            [InlineKeyboardButton(text=t["btn_ref"], callback_data="my_ref")],
            [InlineKeyboardButton(text=t["btn_claim"], callback_data="claim_100")],
            [InlineKeyboardButton(text=t["btn_lang"], callback_data="change_lang")]
        ])
        await message.answer(t["cabinet"].format(coins=coins, tap=tap, refs=refs_count), reply_markup=kb, parse_mode="Markdown")

# To'lov cheklari
@dp.callback_query(F.data == "pay_entry")
async def pay_entry(callback: types.CallbackQuery):
    await callback.message.answer_invoice(
        title="STARS 2X Entry Pass",
        description="Unlock game & earn 100 Stars per 1,000,000 coins",
        payload="entry_50",
        currency="XTR",
        prices=[LabeledPrice(label="Entry Pass", amount=50)]
    )
    await callback.answer()

@dp.callback_query(F.data == "buy_boost")
async def buy_boost(callback: types.CallbackQuery):
    await callback.message.answer_invoice(
        title="2X Multitap Boost",
        description="Double your coins per tap + 1000 max energy",
        payload="boost_25",
        currency="XTR",
        prices=[LabeledPrice(label="2X Boost", amount=25)]
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

# To'lov o'tgandan keyin + Referral bonus berish
@dp.message(F.successful_payment)
async def on_payment_success(message: types.Message):
    payload = message.successful_payment.invoice_payload
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user[1]
    t = TEXTS[lang]

    if payload == "entry_50":
        cursor.execute("UPDATE users SET is_paid = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        await message.answer(t["paid_ok"])

        # Agar kimdir taklif qilgan bo'lsa, unga 50 000 tanga beramiz!
        referrer_id = user[6]
        if referrer_id != 0:
            ref_user = get_user(referrer_id)
            if ref_user:
                cursor.execute("UPDATE users SET coins = coins + 50000, referrals_count = referrals_count + 1 WHERE user_id = ?", (referrer_id,))
                conn.commit()
                try:
                    await bot.send_message(referrer_id, TEXTS[ref_user[1]]["ref_bonus"], parse_mode="Markdown")
                except:
                    pass

        await show_main(message, user_id)

    elif payload == "boost_25":
        cursor.execute("UPDATE users SET multitap = multitap * 2, energy_limit = energy_limit + 1000 WHERE user_id = ?", (user_id,))
        conn.commit()
        await message.answer(t["boost_ok"], parse_mode="Markdown")
        await show_main(message, user_id)

# Referral havolani ko'rsatish
@dp.callback_query(F.data == "my_ref")
async def show_referral(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user(user_id)[1]
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    await callback.message.answer(TEXTS[lang]["ref_text"].format(link=ref_link), parse_mode="Markdown")
    await callback.answer()

# WebApp dan kelgan tangalarni saqlash
@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    new_coins = int(data.get("coins", 0))
    user_id = message.from_user.id
    cursor.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_coins, user_id))
    conn.commit()
    await show_main(message, user_id)

# 1M tangani 100 Starsga almashtirish
@dp.callback_query(F.data == "claim_100")
async def claim_reward(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    lang, coins = user[1], user[3]
    t = TEXTS[lang]

    if coins < 1_000_000:
        await callback.answer(t["not_enough"].format(coins=coins), show_alert=True)
        return

    cursor.execute("UPDATE users SET coins = coins - 1000000 WHERE user_id = ?", (user[0],))
    conn.commit()
    await callback.message.answer(t["claim_ok"], parse_mode="Markdown")
    await bot.send_message(ADMIN_ID, f"💰 **YUTUQ SO'ROVI!**\nUser: @{callback.from_user.username} (`{user[0]}`)\nMukofot: **100 Stars**")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
