import json
from operator import add
import os
import discord
import dotenv
from discord.ext import commands

# Carrega variáveis de ambiente
dotenv.load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

GUILD_ID = 1404890583582900436

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user} (ID: {bot.user.id})')


# Sincroniza comandos de barra
@bot.event
async def setup_hook():
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)


@bot.tree.command(
    name="recreate",
    description="Apaga tudo de um servidor e recria baseado em um JSON válido"
)
async def recreate(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"⚠ Comando recreate solicitado por {interaction.user.name}\n"
        "Tenha em mente que isso apaga tudo no servidor (tudo mesmo)\n"
        "Tem CERTEZA de que deseja continuar?",
        view=ConfirmView(bot)
    )
    bot.comando_recreate = True


    @bot.tree.command(
        name="add",
        description="adiciona cargos, permissões e canais no servidor existente"
    )
    async def add(ctx: discord.Interaction, message: discord.Message):
        await ctx.response.send_message(
            f"⚠ Comando add solicitado por {ctx.user.name}\n"
            "Tenha em mente que isso adiciona cargos, permissões e canais no servidor existente\n"
            "⚠ Isso pode causar conflitos se você não tiver feito backup do servidor\n"
            "Tem CERTEZA de que deseja continuar?",
            view=ConfirmView(bot)
        )
        bot.comando_add = True
        
async def processar_campos(ctx: discord.Interaction, message: discord.Message):
    data = None

    # Se houver anexos, tenta ler o primeiro .txt
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith(".txt"):
            file_bytes = await attachment.read()
            try:
                data = json.loads(file_bytes.decode("utf-8"))
            except json.JSONDecodeError:
                await ctx.channel.send("Arquivo .txt inválido ou não contém JSON válido.")
                return

    # Se não veio arquivo, tenta interpretar o conteúdo da mensagem
    if data is None:
        try:
            data = json.loads(message.content)
        except json.JSONDecodeError:
            await ctx.channel.send("JSON inválido.")
            return

    if getattr(bot, "comando_recreate", False):
        # Apaga todos os canais
        for channel in ctx.guild.channels:
            try:
                await channel.delete()
            except discord.Forbidden:
                await ctx.channel.send(f"Não consegui apagar o canal {channel.name} (permissões insuficientes).")

        # Apaga todos os cargos, exceto @everyone e o próprio cargo do bot
        bot_member = ctx.guild.me
        for role in ctx.guild.roles:
            try:
                if role.name == "@everyone":
                    continue
                if role in bot_member.roles:
                    # Pula o próprio cargo do bot
                    continue
                await role.delete()
            except discord.Forbidden:
                continue

    # Nome do servidor
    if "server_name" in data:
        await ctx.guild.edit(name=data["server_name"])

    # Cargos
    if "roles" in data:
        for role in data["roles"]:
            # Cria um objeto Permissions vazio
            perms = discord.Permissions.none()
            for perm in role.get("permissions", []):
                if hasattr(perms, perm):
                    setattr(perms, perm, True)

            # Converte cor hexadecimal para int
            color_hex = role.get("color", "#000000")
            color_int = int(color_hex.replace("#", ""), 16)

            await ctx.guild.create_role(
                name=role["name"],
                color=discord.Color(color_int),
                permissions=perms
            )

    # Categorias e canais
    if "categories" in data:
        for category in data["categories"]:
            cat = await ctx.guild.create_category(category["name"])
            for channel in category["channels"]:
                overwrites = {}
                for role_name, perms_list in channel.get("overwrites", {}).items():
                    role = discord.utils.get(ctx.guild.roles, name=role_name)
                    if role:
                        po = discord.PermissionOverwrite()
                        for perm in perms_list:
                            if hasattr(po, perm):
                                setattr(po, perm, True)
                        overwrites[role] = po

                if channel["type"] == "text":
                    await ctx.guild.create_text_channel(
                        channel["name"], category=cat, overwrites=overwrites
                    )
                elif channel["type"] == "voice":
                    await ctx.guild.create_voice_channel(
                        channel["name"], category=cat, overwrites=overwrites
                    )





class ConfirmView(discord.ui.View):
    def __init__(self, client: commands.Bot):
        super().__init__(timeout=60)
        self.client = client

    @discord.ui.button(label="✅", style=discord.ButtonStyle.green)
    async def sim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Comando confirmado. Envie o JSON agora.")

        # Espera a próxima mensagem do usuário com JSON
        def check(m: discord.Message):
            return m.author == interaction.user and m.channel == interaction.channel

        message = await interaction.client.wait_for("message", check=check)
        await processar_campos(interaction, message)

    @discord.ui.button(label="❌", style=discord.ButtonStyle.red)
    async def nao(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Comando cancelado.")
        self.client.comando_recreate = False


bot.run(TOKEN)
