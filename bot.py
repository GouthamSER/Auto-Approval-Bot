import os
import random
import asyncio
import threading
from aiohttp import web
from pyrogram import filters, Client, errors, enums, idle
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import UserNotParticipant
from pyrogram.errors.exceptions.flood_420 import FloodWait

# Custom imports (Ensure these files exist in your repository)
from database import add_user, add_group, all_users, all_groups, users, remove_user
from configs import cfg

# Initialize Client
app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Health Check (Render/Koyeb) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

aio_app = web.Application()

async def health(request):
    return web.Response(text="Alive", status=200)

# Add routes for both root and /health to ensure uptime monitors work
aio_app.router.add_get('/', health)
aio_app.router.add_get('/health', health)

def start_aiohttp():
    # Render requires the app to listen on the specific PORT env variable
    # If not found (local testing), it defaults to 8080
    port = int(os.environ.get("PORT", 8080))
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    runner = web.AppRunner(aio_app)
    loop.run_until_complete(runner.setup())
    
    # Listen on 0.0.0.0 to accept external connections
    site = web.TCPSite(runner, '0.0.0.0', port)
    loop.run_until_complete(site.start())
    
    print(f"✅ Health check server started on port {port}")
    loop.run_forever()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Main Process ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, m: Message):
    chat = m.chat
    user = m.from_user
    try:
        add_group(chat.id)
        await app.approve_chat_join_request(chat.id, user.id)
        try:
            await app.send_message(
                user.id, 
                "**Hello {}!\nWelcome To {}\n\n__Powered By : @im_goutham_josh __**".format(user.mention, chat.title)
            )
        except errors.PeerIdInvalid:
            # User hasn't started the bot privately, cannot send DM
            pass
        except Exception as e:
            print(f"DM Error: {e}")
            
        add_user(user.id)
    except Exception as err:
        print(f"Error approving join request: {str(err)}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Start ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.private & filters.command("start"))
async def op(_, m: Message):
    try:
        await app.get_chat_member(cfg.CHID, m.from_user.id)
    except UserNotParticipant:
        try:
            invite_link = await app.create_chat_invite_link(int(cfg.CHID))
            url = invite_link.invite_link
        except Exception:
            # Fallback if bot isn't admin or can't generate link
            url = "https://t.me/wudixh12" 
            
        key = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("🍿 Join Update Channel 🍿", url=url),
                InlineKeyboardButton("🍀 Check Again 🍀", callback_data="check")
            ]]
        )
        await m.reply_text(
            "**⚠️ Access Denied! ⚠️\n\nPlease Join My Update Channel To Use Me.\nIf You Joined The Channel Then Click On Check Again Button To Confirm.**", 
            reply_markup=key
        )
        return

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🗯 Channel", url="https://t.me/wudixh12"),
            InlineKeyboardButton("💬 Support", url="https://t.me/+53lB8qzQaGFlNDll")
        ]]
    )
    add_user(m.from_user.id)
    # Using a fallback photo URL or file_id is safer, ensure the link is valid
    photo_url = "https://ibb.co/LDvYmnSf"
    
    caption_text = "**🦊 Hello {}!\nI'm an auto approve [Admin Join Requests]({}) Bot.\nI can approve users in Groups/Channels.\nAdd me to your chat and promote me to admin with add members permission.\n\n__Powered By : @im_goutham_josh __**".format(m.from_user.mention, "https://t.me/telegram/153")
    
    try:
        await m.reply_photo(photo_url, caption=caption_text, reply_markup=keyboard)
    except Exception:
        # Fallback to text if photo fails
        await m.reply_text(caption_text, reply_markup=keyboard, disable_web_page_preview=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Callback ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_callback_query(filters.regex("check"))
async def chk(_, cb: CallbackQuery):
    try:
        await app.get_chat_member(cfg.CHID, cb.from_user.id)
    except UserNotParticipant:
        await cb.answer("🙅‍♂️ You have not joined my channel. Join first then check again. 🙅‍♂️", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🗯 Channel", url="https://t.me/wudixh12"),
            InlineKeyboardButton("💬 Support", url="https://t.me/+53lB8qzQaGFlNDll")
        ]]
    )
    add_user(cb.from_user.id)
    try:
        await cb.message.delete() # Delete old message for cleaner look
        await app.send_message(
            cb.from_user.id,
            text="**🦊 Hello {}!\nI'm an auto approve [Admin Join Requests]({}) Bot.\nI can approve users in Groups/Channels.\nAdd me to your chat and promote me to admin with add members permission.\n\n__Powered By : @im_goutham_josh __**".format(cb.from_user.mention, "https://t.me/telegram/153"),
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        await cb.answer("Verified! Type /start", show_alert=False)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Info ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("stats") & filters.user(cfg.SUDO))
async def dbtool(_, m: Message):
    xx = all_users()
    x = all_groups()
    tot = int(xx + x)
    await m.reply_text(text=f"""
🍀 **Chats Stats** 🍀
🙋‍♂️ Users : `{xx}`
👥 Groups : `{x}`
🚧 Total : `{tot}` """)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Broadcast ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("broadcast") & filters.user(cfg.SUDO))
async def bcast(_, m: Message):
    if not m.reply_to_message:
        await m.reply("Reply to a message to broadcast.")
        return
    
    lel = await m.reply_text("`⚡️ Processing...`")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    
    # Using find() implies MongoDB. Ensure 'users' is the collection object.
    # If using a cursor, we iterate asynchronously usually, but here iterating strictly
    for usrs in users.find():
        try:
            userid = usrs["user_id"]
            await m.reply_to_message.copy(int(userid))
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            await m.reply_to_message.copy(int(userid))
            success += 1
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(userid)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            # print(e) 
            failed += 1

    await lel.edit(f"✅ Successful: `{success}`\n❌ Failed: `{failed}`\n👾 Blocked: `{blocked}` \n👻 Deactivated: `{deactivated}`")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Broadcast Forward ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("forwardcast") & filters.user(cfg.SUDO))
async def fcast(_, m: Message):
    if not m.reply_to_message:
        await m.reply("Reply to a message to forward.")
        return
    
    lel = await m.reply_text("`⚡️ Processing...`")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    
    for usrs in users.find():
        try:
            userid = usrs["user_id"]
            await m.reply_to_message.forward(int(userid))
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            await m.reply_to_message.forward(int(userid))
            success += 1
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(userid)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            failed += 1

    await lel.edit(f"✅ Successful: `{success}`\n❌ Failed: `{failed}`\n👾 Blocked: `{blocked}` \n👻 Deactivated: `{deactivated}`")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Run ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    # Start the web server in a separate thread
    threading.Thread(target=start_aiohttp, daemon=True).start()
    
    print("🤖 Bot Started! I'm Alive Now!")
    app.run()
