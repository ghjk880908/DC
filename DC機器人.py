import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# --- 🧠 喚醒 Firebase 雲端大腦 ---
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- 外接大腦存取區 (雲端進化版) ---
def load_tools():
    """從 Firebase 讀取大腦記憶"""
    doc_ref = db.collection("bot_data").document("tools")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return {} 

def save_tools(data):
    """把新學到的東西寫進 Firebase 雲端"""
    doc_ref = db.collection("bot_data").document("tools")
    doc_ref.set(data) 

@bot.event
async def on_ready():
    print(f'🔥 {bot.user} 已經上線，【Firebase 雲端大腦】連線成功，準備好當個無情的回話機器了！')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    tools_data = load_tools()
    for keyword, link in tools_data.items():
        if keyword in message.content and not message.content.startswith('!'):
            await message.channel.send(f"找「{keyword}」？拿去吧，這可是該領域的 GOAT 🐐：\n🔗 {link}")
            break 
    await bot.process_commands(message)

# --- 指令區 (一字未刪) ---
@bot.command()
async def 新增(ctx, keyword: str = None, link: str = None):
    if not keyword or not link:
        await ctx.send("欸不是，格式錯了啦！請輸入：`!新增 關鍵字 網址` (中間要有空格)，這樣我才懂好嗎 🙄")
        return
    tools_data = load_tools()
    tools_data[keyword] = link
    save_tools(tools_data)
    await ctx.send(f"✅ 搞定！我現在學會啦～以後誰提到「**{keyword}**」，我就拿 `{link}` 砸他臉上！😎")

@bot.command()
async def 刪除(ctx, keyword: str = None):
    if not keyword:
        await ctx.send("哈囉？你要刪除哪個關鍵字？輸入 `!刪除 關鍵字` 好嗎 🫥")
        return
    tools_data = load_tools()
    if keyword in tools_data:
        del tools_data[keyword]
        save_tools(tools_data)
        await ctx.send(f"🗑️ 已經把「**{keyword}**」從我的大腦裡無情抹除了！再見了酷東西👋")
    else:
        await ctx.send(f"我的記憶庫裡找不到「**{keyword}**」欸，你是不是記錯了？😵‍💫")

@bot.command()
async def 清單(ctx):
    tools_data = load_tools()
    if not tools_data:
        await ctx.send("我現在的大腦空空如也，什麼都沒記住 🫙")
        return
    reply = "📜 **本 Bot 的武林秘笈清單** 📜\n"
    for k, v in tools_data.items():
        reply += f"🔹 **{k}** : <{v}>\n"
    await ctx.send(reply)

@bot.command()
async def 幫幫我(ctx):
    help_text = (
        "🤖 **本群最強工具人 報到！** 🤖\n\n"
        "👉 **自然聊天**：在對話裡提到設定好的關鍵字，我就會丟工具給你。\n"
        "👉 **指定動作**：輸入 `!去背`，馬上獲得神級去背網站。\n"
        "✨ **管理技能**：\n"
        "   `!新增 [關鍵字] [網址]` - 直接教我新招！\n"
        "   `!刪除 [關鍵字]` - 把不要的技能忘掉。\n"
        "   `!清單` - 看看我現在會哪些酷東西。\n"
    )
    await ctx.send(help_text)

@bot.command()
async def 去背(ctx):
    await ctx.send("馬上為您送上神級去背工具：\n🔗 https://tools.dverso.io/bgremove/")

# ⚠️ 記得換成你的 Token
bot.run(os.getenv('BOT_TOKEN'))

