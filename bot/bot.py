import discord
from discord.ext import commands
import os
import sqlite3 as sq
import string
import json

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('Майор Доигралес на месте!')

    global base, cursor
    base = sq.connect("Сurse words.db")
    cursor = base.cursor()
    if base:
        print("Подключение к базе данных произошло успешно")


@bot.event
async def on_member_join(member):
    for chat in bot.get_guild(member.guild.id).channels:
        if chat.name == 'general':
            await bot.get_channel(chat.id).send(f'{member.mention}, здравия желаю, гражданин! '
                                                f'Майор Доигралес следит за порядком в чате. '
                                                f'Чтобы посмотреть правила поведения в чате введите "!инфо"')


@bot.event
async def on_member_remove(member):
    for chat in bot.get_guild(member.guild.id).channels:
        if chat.name == 'general':
            await bot.get_channel(chat.id).send(f'Гражданин {member.mention} отбросил копыта.')


@bot.command()
async def тут(ctx):
    await ctx.send("Майор Доигралес на своём посту! Готов трудиться во имя правопорядка!")


@bot.command()
async def инфо(ctx, *, arg=None):
    user = ctx.message.author
    if arg is None:
        await ctx.send(f'{user.mention} Стоять не двигаться, работает Майор Доигралес! '
                       f'Поставил за вами наружку, мат в чате запрещён! 3 предупреждения - бан! '
                       f'Посмотреть список доступных команд: "!инфо команды"')
    elif arg == 'команды':
        await ctx.send('"!тут" - проверить, на посту ли Майор \n"!досье" - проверить досье на себя')
    else:
        await ctx.send(f'Команда "!инфо {arg}" не поддерживается! Чтобы посмотреть список доступных команд, '
                       f'введите "!инфо команды"')


@bot.command()
async def досье(ctx):
    base.execute('CREATE TABLE IF NOT EXISTS "{}" (user, curse_words_counter)'.format('Curse words data'))
    base.commit()
    user_data = cursor.execute('SELECT * FROM "{}" WHERE user == ?'.format('Curse words data'),
                               (ctx.message.author.id,)).fetchone()
    if user_data is None:
        await ctx.send(f'{ctx.message.author.mention}, у вас пока что нет нарушений')
    else:
        await ctx.send(f'{ctx.message.author.mention}, у вас {user_data[1]} нарушений, соблюдайте закон!')


@bot.event
async def on_message(message):
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split(' ')} \
            .intersection(set(json.load(open('Obscene language.json')))) != set():

        # table_name = 'Curse words data'
        base.execute('CREATE TABLE IF NOT EXISTS "{}" (user, curse_words_counter)'.format('Curse words data'))
        base.commit()

        user_data = cursor.execute('SELECT * FROM "{}" WHERE user == ?'.format('Curse words data'),
                                   (message.author.id,)).fetchone()

        if user_data is None:
            cursor.execute('INSERT INTO "{}" VALUES(?, ?)'.format('Curse words data'), (message.author.id, 1))
            base.commit()
            await message.channel.send(f'{message.author.mention}, за такой базар вам в обезьянник дорога прописана! '
                                       f'Ещё два предупреждения - ответите по закону!')
        elif user_data[1] == 1:
            cursor.execute('UPDATE "{}" SET curse_words_counter == ? WHERE user == ?'.format('Curse words data'),
                           (2, message.author.id))
            base.commit()
            await message.channel.send(f'{message.author.mention}, последнее предупреждение! '
                                       f'Ещё один мат - под шконку отправитесь!')
        elif user_data[1] == 2:
            cursor.execute('UPDATE "{}" SET curse_words_counter == ? WHERE user == ?'.format('Curse words data'),
                           (3, message.author.id))
            base.commit()
            await message.channel.send(f'{message.author.mention}, отправляется валить кругляк')
            await message.author.ban(reason='Много мата (быдло)')

    await bot.process_commands(message)


bot.run(os.getenv('TOKEN'))
