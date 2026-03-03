import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler
import sqlite3, random
import text_loader, time

BOT_TOKEN = "8142912628:AAElW_L5Ffs0Cuj-JMoo7dDYY8xj6HFJnPU"

def make_new_code(user: str):
	conn = sqlite3.connect("user.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM USER WHERE username='"+user+"'")
	if len(cur.fetchall()) == 0:
		rand_code = random.randint(1, 100000)
		cur.execute(f"INSERT INTO USER VALUES ('{user}',{rand_code}, 0)")
		conn.commit()
	conn.close()

def create_refer_link(username: str) -> str:
	conn = sqlite3.connect("user.db")
	cur = conn.execute("SELECT code FROM USER WHERE username='"+username+"'")
	res = cur.fetchall()
	if len(res) != 0:
		res = "https://t.me/bytebazaar_bot?start="+str(res[0][0])
	else:
		res = ""
	conn.close()
	return res

def ignore_insert(username: str, code: int):
	conn = sqlite3.connect("user.db")
	cur = conn.cursor()
	cur.execute(f"INSERT INTO refer (code, username) SELECT {code}, '{username}' WHERE NOT EXISTS (SELECT 1 FROM refer WHERE username='{username}');")
	conn.commit()
	conn.close()

def check_user(username):
	conn = sqlite3.connect("user.db")
	cur = conn.cursor()
	cur.execute("SELECT * FROM USER WHERE username='"+username+"'")
	if len(cur.fetchall()) != 0:
		conn.close()
		return True
	conn.close()
	return False

def get_refer(username):
	conn = sqlite3.connect("user.db")
	cur = conn.cursor()
	cur.execute("SELECT refer FROM USER WHERE username='"+username+"'")
	res = cur.fetchone()
	if len(res) == 0:
		conn.close()
		return -1
	conn.close()
	return res[0]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    keyboard_layout = [
        [KeyboardButton("My Invite Link"), KeyboardButton("Check my refer")],
        [KeyboardButton("Our Customer Service")]
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard_layout,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    
    if context.args:
        code = context.args[0]
        if not check_user(username):
            ignore_insert(username, code)
            make_new_code(username)
            kb = [
                [InlineKeyboardButton("Best Poem",url="https://t.me/WhentheMoonSawMeAloneAgain")],
                [InlineKeyboardButton("ByteBazaar",url="https://t.me/bytebazaarshop")]
            ]
            rp = InlineKeyboardMarkup(kb)
            await update.message.reply_text(
                "Please Join our main channel",
                reply_markup=rp
            )
        else:
            await update.message.reply_text(
                "You are already member",
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_text(
            text_loader.intro_text(),
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	if hasattr(update.message, 'text'):
		user_text = update.message.text
		username = update.effective_user.username
		if user_text == "My Invite Link":
			link = create_refer_link(username)
			if link != "":
				await update.message.reply_text(text_loader.refer_text(link))
			else:
				await update.message.reply_text("You are not member")
		elif user_text == "Check my refer":
			count = get_refer(username)
			if count >= 0:
				await update.message.reply_text(f"You have {count} refer point✨")
			else:
				await update.message.reply_text(f"Something went wrong")
		elif user_text == "Our Customer Service":
			kb = [
				[InlineKeyboardButton("Customer Service", url="http://t.me/Bytebazzar_HrManager")]
			]
			reply_markup = InlineKeyboardMarkup(kb)
			await update.message.reply_text(text_loader.CS_text(), reply_markup=reply_markup)
		else:
			await update.message.reply_text(f"I don't understand '{user_text}'. Please use the keyboard.")
	else:
		message = update.channel_post
		ch_id = message.chat.id
		text = message.text
		print(ch_id,"->",text)

async def Chat_Mem_Handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	new_member = update.chat_member
	if new_member.new_chat_member.status == "member":
		username = update.effective_user.username
		conn = sqlite3.connect("user.db")
		cur = conn.cursor()
		if username != None:	
			cur.execute("SELECT code FROM refer WHERE username='"+username+"'")
			res = cur.fetchall()
			if len(res) == 0:
				conn.close()
				return 0
			for code in res:
				cur.execute(f"UPDATE USER SET refer=refer+1 WHERE code={code[0]}")
				cur.execute(f"DELETE FROM refer WHERE username='{username}'")
			conn.commit()
		conn.close()
	# print(new_member)

def main() -> None:
	application = Application.builder().token(BOT_TOKEN).build()
	application.add_handler(CommandHandler("start", start))
	application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
	application.add_handler(ChatMemberHandler(Chat_Mem_Handler, ChatMemberHandler.CHAT_MEMBER))
	# Run the bot until you press Ctrl-C
	print("Bot is running...")
	while 1:
		try:
			application.run_polling(allowed_updates=Update.ALL_TYPES)
		except KeyboardInterrupt:
			print("Bot killed")
			break
		except:
			print("*****\nError Happen in main loop, retrying after 5 sec....\n*****")
			time.sleep(5)
			continue


if __name__ == "__main__":

    main()
