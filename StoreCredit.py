import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
import json
import os
import random
import string
import re
import emoji

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

class ViewPersistence(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="$", intents=discord.Intents.all(), description="Your best Exchange supporter 💜")

    async def setup_hook(self):  
        self.add_view(ButtonToOpenMMTicket())
    
    

client = ViewPersistence()
bot = client


@client.event
async def on_ready():
    print(f"The bot is ready, logged in as {client.user}")

    try:
        synced = await client.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


file_name = "StoreCredit.json"


def load_credits():
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            
            return {}
    return {}


def save_credits(credits):
    with open(file_name, 'w') as f:
        json.dump(credits, f, indent=4)

def load_credits():
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
           
            return {}
    return {}


@bot.tree.command(name="tip", description="Tip your Store Credit to someone else")
@app_commands.describe(user="The user to tip the store credit to", amount="How much do you want to tip?")
async def tipCommand(interaction: discord.Interaction, user: discord.Member, amount: str):
    
    amount = amount.replace('.', ',')


    try:
        amount = float(amount.replace(',', '.'))  
    except ValueError:
        await interaction.response.send_message("Invalid amount format. Please use numbers like '123,45'.", ephemeral=True)
        return

    credits = load_credits()


    tipper_id = str(interaction.user.id)
    recipient_id = str(user.id)


    tipper_credit = credits.get(tipper_id, 0.0)
    if tipper_credit < amount:

        await interaction.response.send_message(f"You do not have enough store credit to tip {amount:.2f}. Your current credit is {tipper_credit:.2f}.", ephemeral=True)
        return

    credits[tipper_id] -= amount

   
    if recipient_id in credits:
        credits[recipient_id] += amount
    else:
        credits[recipient_id] = amount

    save_credits(credits)

    formatted_amount = f"{amount:.3f}".replace(',', '.')
    formatted_tipper_total = f"{credits[tipper_id]:.3f}".replace(',', '.')
    formatted_recipient_total = f"{credits[recipient_id]:.3f}".replace(',', '.')

    # await interaction.response.send_message(f"You have successfully tipped {formatted_amount} store credit to {user.mention}. Your new balance is {formatted_tipper_total}.", ephemeral=True)

    await interaction.response.send_message(
    embed=discord.Embed(
        title="💸 Tipped Successfully!",
        description=f"You have tipped {user.mention} successfully!",
        color=discord.Color.green()  
    )
    .add_field(name="💵 Amount Tipped", value=f"**${formatted_amount}**", inline=False)
    .add_field(name="Your New Balance", value=f"**${formatted_tipper_total}**", inline=True)
    .add_field(name=f"{user.display_name}'s New Balance", value=f"**${formatted_recipient_total}**", inline=True)
    .set_thumbnail(url=user.display_avatar.url) 
    .set_footer(text="Thank you for using the Store Credit system! 😊", icon_url=interaction.user.display_avatar.url),  
    ephemeral=True
        )


    channel = bot.get_channel(1281738288423506033)
    await channel.send(f"{interaction.user.mention} has tipped {formatted_amount} Store Credit to {user.mention}. {user.mention} now has {formatted_recipient_total} Store Credit.")



store_credit_file = "StoreCredit.json"
money_file = "Money.json"

@bot.tree.command(name="wallet", description="See your or other people's stats")
@app_commands.describe(user="The user to fetch stats for (optional)")
async def statsCommand(interaction: discord.Interaction, user: discord.Member = None):
   
    if user is None:
        user = interaction.user

  
    store_credits = load_json(store_credit_file)
    money_data = load_json(money_file)

  
    user_id = str(user.id)

 
    user_store_credit = store_credits.get(user_id, 0.0)
    user_money = money_data.get(user_id, 0.0)

    formatted_store_credit = f"{user_store_credit:.3f}".replace(',', '.')
    formatted_money = f"{user_money:.3f}".replace(',', '.')

   
    embed = discord.Embed(
        title=f"💼 {user.display_name}'s Wallet",
        color=discord.Color.green()  
    )
    embed.add_field(name="💳 Store Credit", value=f"**${formatted_store_credit}**", inline=False)
    embed.add_field(name="💵 Money", value=f"**${formatted_money}**", inline=False)
    embed.set_thumbnail(url=user.display_avatar.url) 
    embed.set_footer(text="Manage your Balance wisely!", icon_url=user.display_avatar.url)  

   
    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="leaderboard", description="Shows the top 10 people who have Store Credit")
async def leaderboardCommand(interaction: discord.Interaction):
   
    credits = load_credits()

   
    sorted_credits = sorted(credits.items(), key=lambda x: x[1], reverse=True)

   
    embed = discord.Embed(
        title="🏆 Store Credit Leaderboard 🏆",
        description="Here are the top users with the most store credits!",
        color=discord.Color.gold()
    )

   
    max_users = 10

    if not sorted_credits:
        embed.add_field(name="No users found", value="The leaderboard is currently empty.", inline=False)
    else:
     
        for index, (user_id, credit) in enumerate(sorted_credits[:max_users], start=1):
           
            user = await bot.fetch_user(int(user_id))
            formatted_credit = f"{credit:.3f}".replace(',', '.')
            embed.add_field(
                name=f"{index}. {user.display_name}",
                value=f"{formatted_credit} credits",
                inline=False
            )

   
    await interaction.response.send_message(embed=embed)


codes_file = "codes.json"

def load_json(file_path):
    """Load JSON data from a file, returns an empty dict if file is not found or is invalid."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_json(file_path, data):
    """Save data to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def generate_code(length=10):
    """Generate a random alphanumeric code of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@bot.tree.command(name="generate", description="Generate a unique Affiliate code.")
async def generate_code_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    codes = load_json(codes_file)
 

    if user_id in codes:
        await interaction.response.send_message("You already have a code. Please use ``/code`` to see your code.", ephemeral=True)
        return

    code = generate_code()


    codes[user_id] = code
    save_json(codes_file, codes)

    await interaction.response.send_message(f"Your unique code is: **{code}**", ephemeral=True)

@bot.tree.command(name="code", description="Use this to see your Affiliate code")
async def codeCommandSeing(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    

    codes = load_json(codes_file)

    if user_id in codes:
        code = codes[user_id]
        await interaction.response.send_message(
            embed=discord.Embed(
                title="🎫 Your Affiliate Code",
                description=f"Your unique affiliate code is: **{code}**",
                color=discord.Color.blue()  
            ),
            ephemeral=True  
        )
    else:
        await interaction.response.send_message(
            "You do not have an affiliate code. Please generate one using the `/generate` command.",
            ephemeral=True
        )

Authorized_users = {929655970576089128, 530425206347530250} # ivak and smasher

@bot.tree.command(name="code_owner", description="See who owns what code")
@app_commands.describe(code="Write the code to see who owns it", user="Choose a user to see what code they have")
async def code_owner(interaction: discord.Interaction, code: str = None, user: discord.Member = None):


    if code and user:
        embed = discord.Embed(
            title="⚠️ Invalid Input",
            description="Please provide only one parameter: either a Affiliate code or a user, not both.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    codes = load_json(codes_file)

    if code:
      
        owner = next((user_id for user_id, user_code in codes.items() if user_code == code), None)
        if owner:
            owner_user = await bot.fetch_user(int(owner))
            embed = discord.Embed(
                title="🔍 Affiliate Code Lookup",
                description=f"The Affiliate code **{code}** is owned by {owner_user.mention}.",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title="❌ Affiliate Code Not Found",
                description=f"No user found with the Affiliate code **{code}**.",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    elif user:
        user_id = str(user.id)
       
        user_code = codes.get(user_id, None)
        if user_code:
            embed = discord.Embed(
                title="🔍 User Affiliate Code",
                description=f"{user.mention} has the Affiliate code: **{user_code}**.",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title="❌ No Affiliate Code Found",
                description=f"{user.mention} does not have a Affiliate code.",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="money", description="Used to add money to someone")
@app_commands.describe(user="The user to DM that they got money", amount="The amount they should get")
async def AddingMoneyToUser(interaction: discord.Interaction, user: discord.Member, amount: str):
    if interaction.user.id in Authorized_users:
        try:
         
            amount = amount.replace('.', ',')

            try:
                amount = float(amount.replace(',', '.'))  
            except ValueError:
                await interaction.response.send_message("Invalid amount format. Please use numbers like '123,45'.", ephemeral=True)
                return

          
            money_data = load_json(money_file)

         
            user_id = str(user.id)

        
            if user_id in money_data:
                money_data[user_id] += amount
            else:
                money_data[user_id] = amount

          
            save_json(money_file, money_data)

           
            embed = discord.Embed(
                title="💸 You Received Money!",
                description=(
                    f"Hello {user.mention},\n\n"
                    f"🎉 Congratulations! You have just received **${amount:.2f}** from your Affiliate code.\n\n"
                    f"**How to Check Your Balance:**\n"
                    f"Use the command `/wallet` to view your current balance.\n\n"
                    f"**How to Withdraw Your Money:**\n"
                    f"1. Use the command `/withdraw` in the **PS99 Marketplace**.\n"
                    f"2. Provide your **LTC address**. Please ensure it is your address, as refunds cannot be processed.\n"
                    f"3. You will receive a notification after we have sent the money to the LTC address you gave us.\n\n"
                    f"If you have any questions, feel free to reach out!"
                ),
                color=discord.Color.green()  
            )
            embed.set_thumbnail(url=user.display_avatar.url)  
            embed.set_footer(text="Enjoy your free Money 💵", icon_url=user.display_avatar.url)  

         
            await user.send(embed=embed)


            await interaction.response.send_message(
                embed=discord.Embed(
                    title="💸 **Transaction Successful!**",
                    description=f"**Message sent to:** {user.mention}\n"
                                f"**Added Balance:** `${amount:.2f}` 💵",
                    color=discord.Color.green()
                )
                .set_footer(text="Money successfully added!"),
                ephemeral=True)


        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
    else:
        await interaction.response.send_message(f"You dont have permissions to use this", ephemeral=True)

    
@bot.tree.command(name="withdraw", description="Used to withdraw ALL of your money. LTC only")
@app_commands.describe(address="Please provide your LTC address here")
async def WithdrawingMoneyBalance(interaction: discord.Interaction, address: str):
    user_id = str(interaction.user.id)
    
 
    money_data = load_json(money_file)

    if user_id in money_data and money_data[user_id] > 0:
     
        total_money = money_data[user_id]

       
        

        await interaction.response.send_message(
            embed=discord.Embed(
                title="📢 **Owners Notified!**",
                description=(
                    "🚀 The **owners** have been notified about your withdrawal request!\n\n"
                    "⏳ *Please be patient as this process may take some time.*\n\n"
                    "📬 You will receive a DM once the LTC has been sent to the LTC address you provided!"
                ),
                color=discord.Color.green()
            )
            .set_footer(text="Thank you for your patience! We'll update you soon."),
            ephemeral=True)


      
        channel = bot.get_channel(1281738288423506033)

      
        embed = discord.Embed(
            title="Withdraw Request",
            description=(
                f"The user {interaction.user.mention} wants to withdraw their total balance of "
                f"**${total_money:.2f}** to the LTC address: **{address}**"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Please use /sent_money after you have sent the money to the LTC address.", icon_url=interaction.user.display_avatar.url)
        
       
        await channel.send(embed=embed, content=f"<@929655970576089128>")

      
        del money_data[user_id]
        save_json(money_file, money_data)

    else:
       
        await interaction.response.send_message("You don't have any Money balance.", ephemeral=True)


@bot.tree.command(name="sent_money", description="Notify a user that their money has been sent to their LTC address.")
@app_commands.describe(user="The user to notify about the sent money")
async def sent_money_notification(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id in Authorized_users:
       
        

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ **User Notified!**",
                description=(
                    f"📨 The user {user.mention} has been **notified** that their "
                    f"💰 **Money balance** has been successfully withdrawn."
                ),
                color=discord.Color.green()
            )
            .set_footer(text="User has been notified."),
            ephemeral=True)


      
        embed = discord.Embed(
            title="💸 Your Money Has Been Sent!",
            description=(
                f"Hello {user.mention},\n\n"
                f"🎉 The money you requested has been successfully sent to the LTC address you provided. "
                f"Thank you for your patience!\n\n"
                f"**Please Take Note:**\n"
                f"- Please leave a vouch in the following channel: [Public Vouches Channel](https://discord.com/channels/806112438948462592/966608766793547786).\n"
                f"- Include a screenshot of the transaction for confirmation.\n\n"
                f"We appreciate your cooperation and hope you have a great day!"
            ),
            color=discord.Color.green()  
        )

      

        embed.set_footer(text="Thank you for using our service!", icon_url=user.display_avatar.url) 
       
        await user.send(embed=embed)
    else:
        await interaction.response.send_message("You dont have permission to do this", ephemeral=True)

@bot.tree.command(name="help", description="List of all commands")
async def help_command(interaction: discord.Interaction):
   
    embed = discord.Embed(
        title="**📖 Help & Commands**",
        description="Here is a list of all available commands to help you use the bot more effectively:",
        color=discord.Color.green()  
    )

   
    embed.add_field(
    name="🌐 **Public Commands**",
    value=(
        "• **/tip** - 💸 *Tip someone your Store Credit.*\n"
        "• **/wallet** - 👛 *Shows your wallet or someone else's.*\n"
        "• **/leaderboard** - 🏆 *Displays the top 10 Store Credit holders.*\n"
        "• **/generate** - 🔄 *Generate a one-time Affiliate code.*\n"
        "• **/code_owner** - 🕵️‍♂️ *Find who owns a code or what code belongs to whom.*\n"
        "• **/code** - 🔍 *View your own Affiliate code.*\n"
        "• **/withdraw** - 💵 *Withdraw your MONEY BALANCE. The entire amount will be withdrawn, and you'll be notified upon completion.*\n"
        "• **/wheel** - 🎡 *Spin the monthly wheel. If won, you will get a **FREE SHOP** for 30 Days.*\n"
        "• **/help** - ❓ *Displays this help message.*\n"
        "• **/ping-shop** - 🔔 *Notify the 'shop ping' role. Costs 1 Store Credit.*\n"
        "• **/ping-everyone** - 📢 *Send a notification to everyone in the server. Costs 3 Store Credit.*"
    ),
        inline=False
    )

   
    embed.add_field(
        name="🔒 **Private Commands**",
        value=(
            "• **/money** - 💰 *Add Money Balance to someone.*\n"
            "• **/sent_money** - ✅ *Confirm when LTC has been sent.*\n"
            "• **/close** - 📜 *Closes a ticket and generates a transcript for a MM Ticket.*\n"
            "• **/add** - ➕ *Adds a user to a MM Ticket.*\n"
            "• **/remove** - ➖ *Removes a user from a MM Ticket.*"
        ),
        inline=False
    )

 
    embed.set_footer(text="Use these commands wisely!", icon_url=interaction.user.display_avatar.url)


  
    await interaction.response.send_message(embed=embed)



wheel_data_file = "wheel_data.json"

def load_wheel_data():
    try:
        with open(wheel_data_file, "r") as f:
            content = f.read().strip() 
            if not content: 
                return {} 
            return json.loads(content) 
    except FileNotFoundError:
        
        return {}
    except json.JSONDecodeError:
        
        return {}


def save_wheel_data(data):
    with open(wheel_data_file, "w") as f:
        json.dump(data, f)


@bot.tree.command(name="wheel", description="Spin the wheel for a chance to win! (Monthly)")
@app_commands.describe(chosen_number="Choose a number between 1 and 250")
async def spin_wheel(interaction: discord.Interaction, chosen_number: int):
    if chosen_number < 1 or chosen_number > 250:
        await interaction.response.send_message(
            "Please choose a number between 1 and 250.",
            ephemeral=True
        )
        return

    wheel_data = load_wheel_data()
    user_id = str(interaction.user.id)
    current_month = datetime.now().strftime("%Y-%m")

    if user_id in wheel_data and wheel_data[user_id] == current_month:
        await interaction.response.send_message(
            "You've already spun the wheel this month! Try again next month.",
            ephemeral=True
        )
        return

    wheel_data[user_id] = current_month
    save_wheel_data(wheel_data)

    await interaction.response.defer(thinking=True)

    winning_number = random.randint(1, 250)
    wheel_values = [random.randint(1, 250) for _ in range(10)]
    
   
    embed = discord.Embed(
        title="🎡 Spinning the Wheel...",
        description="Get ready for the result!",
        color=discord.Color.blue()
    )
    wheel_message = await interaction.followup.send(embed=embed)

    for value in wheel_values:
        await asyncio.sleep(1)
        embed.description = f"Spinning the wheel... {value}"
        await wheel_message.edit(embed=embed)

    await asyncio.sleep(1)
    embed.description = f"Spinning the wheel... {winning_number}"
    await wheel_message.edit(embed=embed)

    win = chosen_number == winning_number

    result_embed = discord.Embed(
        title="🎉 We Have a Winner! 🎉" if win else "Better Luck Next Time!",
        description=f"{interaction.user.mention} {'has won the monthly wheel spin with number ' + str(chosen_number) if win else 'did not win this month. Try again next month!\n\n The winning number was ' + str(winning_number)}",
        color=discord.Color.gold() if win else discord.Color.red()
    )
    result_embed.set_thumbnail(url=interaction.user.display_avatar.url)

   
    await wheel_message.edit(embed=result_embed)

    if win:
        win_channel_id = 1281738288423506033
        win_channel = bot.get_channel(win_channel_id)
        if win_channel:
            await win_channel.send("<@929655970576089128>")
            await win_channel.send(embed=result_embed)


@bot.command()
async def Sending_Buttons_MM(ctx):
    await ctx.send(embed=discord.Embed(
    title="🔒 **Middleman Service**",
    description=(
        "👋 **Hello!**\n\n"
        "Welcome to our **Middleman Ticket System**! Please choose the option that matches the value of your trade in USD.\n\n"
        "**📌 Important Notes:**\n"
        "• Our Middleman service is **free** for trades under **$50**.\n"
        "• For trades over **$50**, a **1% fee** will be applied."
    ),
    color=discord.Color.from_rgb(0, 255, 0)
), view=ButtonToOpenMMTicket())


def load_open_tickets_data():
    try:
        with open("OpenMM.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_open_tickets_data(data):
    with open("OpenMM.json", "w") as f:
        json.dump(data, f)

class TicketInfoModal(discord.ui.Modal, title="Ticket Information"):
    seller = discord.ui.TextInput(label="Who is the seller?", placeholder="Please write here the person who SELLS the stuff", required=True, max_length=99, style=discord.TextStyle.short)
    buyer = discord.ui.TextInput(label="Who is the buyer?", placeholder="Please write here the person who BUYS the stuff", required=True, max_length=99, style=discord.TextStyle.short)
    other_person = discord.ui.TextInput(label="Other user", placeholder="Please write the user or userid of the other person", required=True, max_length=99, style=discord.TextStyle.short)
    trade_details = discord.ui.TextInput(label="What is the FULL trade?", placeholder="e.g. 10b PS99 gems for 100$ LTC", required=True, max_length=99, style=discord.TextStyle.short)
    trade_part = discord.ui.TextInput(label="What do you have?", placeholder="e.g. 10b gems (what side of the trade u have)", required=True, max_length=99, style=discord.TextStyle.short)

    def __init__(self, view, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_name = interaction.user.name
        guild = interaction.guild
        channel_name = f"ticket-{user_name}"
        category_name = "tickets"

       
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)

       
        role1 = discord.utils.get(guild.roles, name="Large Trade MM (no $ cap)")
        role2 = discord.utils.get(guild.roles, name="Head MM ($0 - $225)")
        role3 = discord.utils.get(guild.roles, name="Senior MM ($0 - $125)")
        role4 = discord.utils.get(guild.roles, name="MiddleMan ($0 - $50)")
        role5 = discord.utils.get(guild.roles, name="Trial MM ($0 - $20)")

       
        TrialMM = UserPingingChannel[interaction.user.id]["number"]

        if TrialMM == 1:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True, attach_files = True),
                role1: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role2: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role3: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role4: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role5: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
            }
        elif TrialMM == 2:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True, attach_files = True),
                role1: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role2: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role3: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role4: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role5: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
            }
        elif TrialMM == 3:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True, attach_files = True),
                role1: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role2: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role3: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role4: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
                role5: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
            }
        elif TrialMM == 4:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True, attach_files = True),
                role1: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role2: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role3: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
                role4: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
                role5: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
            }
        elif TrialMM == 5:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True, attach_files = True),
                role1: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=False),
                role2: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
                role3: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
                role4: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
                role5: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
            }
        else:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True, attach_files = True),
                role1: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
                role2: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
                role3: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
                role4: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
                role5: discord.PermissionOverwrite(view_channel=False, read_messages=False, send_messages=False),
            }

       
        ticket_channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)

       
        await interaction.response.send_message(f"Ticket channel {ticket_channel.mention} created!", ephemeral=True)

      
        await ticket_channel.send(f"Welcome {interaction.user.mention}! Please wait till a Middle man is on their way!")

      
        embed = discord.Embed(
            title="💼 MM Information",
            description=f"**Here is the information provided by** {interaction.user.mention}:",
            color=discord.Color.from_rgb(0, 255, 0)
        )

     
        embed.add_field(name="🛒 Seller:", value=f"```{self.seller.value}```", inline=False)
        embed.add_field(name="👤 Buyer:", value=f"```{self.buyer.value}```", inline=False)
        embed.add_field(name="🔄 Other Person:", value=f"```{self.other_person.value}```", inline=False)
        embed.add_field(name="📜 Full Trade Details:", value=f"```{self.trade_details.value}```", inline=False)
        embed.add_field(name="📦 User's Trade Part:", value=f"```{self.trade_part.value}```", inline=False)

        embed.set_footer(text="Ticket created by the bot.")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        

        if TrialMM == 1:
            message = "<@&1039721037702631455> <@&995451774389461112>"
        elif TrialMM == 2:
            message = "<@&995451774389461112> <@&1053164380382036008>"
        elif TrialMM == 3:
            message = "<@&1053164380382036008> <@&1053164778975141961>"
        elif TrialMM == 4:
            message = "<@&1053164778975141961> <@&1053164892158435338>"
        elif TrialMM == 5:
            message = "<@&1053164892158435338>"

        await ticket_channel.send(embed=embed)
        await ticket_channel.send(f"{message}\n", view=ClaimMMTicket())

        open_tickets_data = load_open_tickets_data()
        open_tickets_data[user_id] = {
            "user_name": user_name,
            "channel_id": str(ticket_channel.id)
        }
        save_open_tickets_data(open_tickets_data)

UserPingingChannel = {}

class ButtonToOpenMMTicket(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Trades under $20", style=discord.ButtonStyle.blurple, custom_id="button_under_20")
    async def UndertwentyButton(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_button_click(interaction)
        UserPingingChannel[interaction.user.id] = {"number": 1}

    @discord.ui.button(label="$21 - $50 Trade", style=discord.ButtonStyle.grey, custom_id="button_21_to_50")
    async def TwentyonetofiftyButton(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_button_click(interaction)
        UserPingingChannel[interaction.user.id] = {"number": 2}

    @discord.ui.button(label="$51 - $125 Trade", style=discord.ButtonStyle.blurple, custom_id="button_51_to_125")
    async def FiftyonetoonetwentyfiveButton(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_button_click(interaction)
        UserPingingChannel[interaction.user.id] = {"number": 3}

    @discord.ui.button(label="$126 - $225 Trade", style=discord.ButtonStyle.grey, custom_id="button_126_to_225")
    async def OnehundredtwentysixToTwohundredtwentyfiveButton(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_button_click(interaction)
        UserPingingChannel[interaction.user.id] = {"number": 4}

    @discord.ui.button(label="Above $226 Trade", style=discord.ButtonStyle.blurple, custom_id="button_above_226")
    async def AboveTwohundredtwentysixButton(self, interaction: discord.Interaction, button: discord.Button):
        await self.handle_button_click(interaction)
        UserPingingChannel[interaction.user.id] = {"number": 5}

    
    async def handle_button_click(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        open_tickets_data = load_open_tickets_data()

        if user_id in open_tickets_data:
            await interaction.response.send_message("You can't open a ticket since one is already open. If it isn't, please ping a staff member.", ephemeral=True)
        else:
            
            await interaction.response.send_modal(TicketInfoModal(self))

claimed_tickets = {}

class ClaimMMTicket(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.green, custom_id="ClaimingTicketYa")
    async def CLaimingMMTicket(self, interaction: discord.Interaction, button: discord.Button):
        required_role_ids = {
            1039721037702631455,  
            995451774389461112,  
            1053164380382036008,  
            1053164778975141961, 
            1053164892158435338  
        }
        user = interaction.user
        channel = interaction.channel

      
        if not any(role.id in required_role_ids for role in user.roles):
            await interaction.response.send_message("You don't have the necessary permissions to claim this ticket.", ephemeral=True)
            return

       
        if interaction.user.id not in claimed_tickets:
            claimed_tickets[interaction.user.id] = {'channel_id': interaction.channel.id}

         
            button.disabled = True
            await interaction.message.edit(view=self)
            await interaction.response.send_message(f"{user.mention} has claimed this ticket and is your MM now.", ephemeral=False)

           
            role_permissions = {
                1039721037702631455: discord.PermissionOverwrite(view_channel=False),  
                995451774389461112: discord.PermissionOverwrite(view_channel=False),  
                1053164380382036008: discord.PermissionOverwrite(view_channel=False),  
                1053164778975141961: discord.PermissionOverwrite(view_channel=False),  
                1053164892158435338: discord.PermissionOverwrite(view_channel=False),
                966727792505020436: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True),
                1025793058945646642: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True),
                832554814721753109: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True)
            }

          
            for role_id, permissions in role_permissions.items():
                role = discord.utils.get(interaction.guild.roles, id=role_id)
                if role:
                    await channel.set_permissions(role, overwrite=permissions)

          
            await channel.set_permissions(user, overwrite=discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True, attach_files = True))
        
        else:
            await interaction.response.send_message(f"{interaction.user.mention}, you have already claimed a ticket.", ephemeral=True)




@client.tree.command(name="remove", description="removes a User in a Ticket")
@app_commands.describe(target_user_id="Who should be removed? USERID ONLY")
async def remove(interaction: discord.Interaction, target_user_id: str):
    required_role_ids = {
            1039721037702631455,  
            995451774389461112,  
            1053164380382036008,  
            1053164778975141961, 
            1053164892158435338  
        }

    user = interaction.user
    channel = interaction.channel

    if channel.name.startswith("ticket"):

   
        if not any(role.id in required_role_ids for role in user.roles):
            await interaction.response.send_message("You don't have the necessary permissions to add someone in this ticket.", ephemeral=True)
            return
        
        try:
            target_user_id = int(target_user_id)
        except ValueError:
            await interaction.response.send_message("Invalid user ID. Please provide a valid number.")
            return
        
        await interaction.channel.set_permissions(interaction.guild.get_member(target_user_id), view_channel = False, send_messages = False, attach_files = False)
        
        embed = discord.Embed(
            title=f"Member has been removed",
            description=f"The Member <@{target_user_id}> was removed.",
            color = discord.Color.from_rgb(255,0,0)
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("This is not a ticket", ephemeral=True)

@client.tree.command(name="add", description="adds a User in a Ticket")
@app_commands.describe(target_user_id="Who should be added? USERID ONLY")
async def addinguserinticket(interaction: discord.Interaction, target_user_id: str):
    
    required_role_ids = {
            1039721037702631455,  
            995451774389461112,  
            1053164380382036008,  
            1053164778975141961, 
            1053164892158435338  
        }

    user = interaction.user
    channel = interaction.channel

    if channel.name.startswith("ticket"):

   
        if not any(role.id in required_role_ids for role in user.roles):
            await interaction.response.send_message("You don't have the necessary permissions to claim this ticket.", ephemeral=True)
            return
        
        try:
            target_user_id = int(target_user_id)
        except ValueError:
            await interaction.response.send_message("Invalid user ID. Please provide a valid number.")
            return
        
        await interaction.channel.set_permissions(interaction.guild.get_member(target_user_id), view_channel = True, send_messages = True, attach_files = True)
        
        embed = discord.Embed(
            title=f"Member has been added",
            description=f"The Member <@{target_user_id}> was added.",
            color = discord.Color.from_rgb(0,255,0)
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("This is not a ticket", ephemeral=True)


@client.tree.command(name="close", description="Closes the MM ticket")
async def transcript(interaction: discord.Interaction):
    required_role_ids = {
            1039721037702631455,  
            995451774389461112,  
            1053164380382036008,  
            1053164778975141961, 
            1053164892158435338  
        }
    
    user = interaction.user
    
    if "ticket" in interaction.channel.name:
        if not any(role.id in required_role_ids for role in user.roles):
            await interaction.response.send_message("You don't have the necessary permissions to create a transcript for this ticket.", ephemeral=True)
            return
        
        transcript_channel_id = 1273341411563012208 
        transcript_channel = interaction.guild.get_channel(transcript_channel_id)
        
        if os.path.exists(f"{interaction.channel.name}.md"):
            os.remove(f"{interaction.channel.name}.md")
        
        with open(f"{interaction.channel.name}.md", 'a', encoding='utf-8') as f:
            f.write(f"# Transcript of {interaction.channel.name}:\n\n")
            async for message in interaction.channel.history(limit=None, oldest_first=True):
                created = datetime.strftime(message.created_at, "%m/%d/%Y at %H:%M:%S")
                
                if message.attachments:
                    image_links = "\n".join(attachment.url for attachment in message.attachments)
                    f.write(f"{message.author} on {created}: Sent image(s) or Video(s):\n{image_links}\n")
                else:
                    if message.edited_at:
                        edited = datetime.strftime(message.edited_at, "%m/%d/%Y at %H:%M:%S")
                        content = replace_emojis(message.clean_content)
                        f.write(f"{message.author} on {created}: {content} (Edited at {edited})\n")
                    else:
                        content = replace_emojis(message.clean_content)
                        f.write(f"{message.author} on {created}: {content}\n")

            generated = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
            f.write(f"\n*Generated at {generated} by {client.user}*\nDate Formatting: MM/DD/YY*\n*Time Zone: UTC*")
        
        with open(f"{interaction.channel.name}.md", 'rb') as f:
            await transcript_channel.send(file=discord.File(f, f"{interaction.channel.name}.md"))
        
        os.remove(f"{interaction.channel.name}.md")
        await interaction.response.send_message(f"{interaction.user.mention} are you sure to close the Ticket? Please press the Button ``close`` under this message to confirm.\n\nTranscript has been saved.",view=CloseButton(), ephemeral=False)
        
    else:
        await interaction.response.send_message("This isn't a ticket!", ephemeral=True)

def replace_emojis(text):
    def replace(match):
        emoji_unicode = match.group()
        try:
            emoji_name = emoji.demojize(emoji_unicode).replace(":", "")
            if emoji_unicode.startswith("<a:"): 
                emoji_unicode = f"\\U{emoji_name.split(':')[2]}"
            elif emoji_unicode.startswith("<:"):  
                emoji_unicode = f"\\U{emoji_name.split(':')[1]}"
            else:
                emoji_unicode = emoji.emojize(f":{emoji_name}:", use_aliases=True)
                emoji_unicode = emoji_unicode.encode('unicode-escape').decode('utf-8')
        except:
            pass
        return emoji_unicode

    return re.sub(r"<a?:[a-zA-Z0-9_]+:[0-9]+>|:[a-zA-Z0-9_]+:", replace, text)

class CloseButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, custom_id="lalalalallasdasdw")
    async def onclosingmmticketfrfr(self, interaction: discord.Interaction, button: discord.Button):
        required_role_ids = {
            1039721037702631455,  
            995451774389461112,  
            1053164380382036008,  
            1053164778975141961, 
            1053164892158435338  
        }

        open_tickets_data = load_open_tickets_data()

        ticket_creator_id = None
        for user_id, info in open_tickets_data.items():
            if info["channel_id"] == str(interaction.channel.id):
                ticket_creator_id = user_id  
                break

        
        if not any(role.id in required_role_ids for role in interaction.user.roles):
            await interaction.response.send_message("You don't have the necessary permissions to close this ticket.", ephemeral=True)
            return

       
        if interaction.user.id in claimed_tickets:
            ticket_info = claimed_tickets[interaction.user.id]
            if ticket_info['channel_id'] == interaction.channel.id:
             
                await interaction.response.send_message(embed=discord.Embed(
                    title="Closing",
                    description="This channel will be closed in 5 seconds...",
                    color=discord.Color.red() 
                ))

                await asyncio.sleep(5)  

               
                await interaction.channel.delete()

            
                del claimed_tickets[interaction.user.id]
            else:
                await interaction.response.send_message("You cannot close this ticket as it is not the one you claimed.", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"{interaction.user.mention}, you can't close this ticket since you don't have any claimed.", ephemeral=True)
            return

        if ticket_creator_id:
            if ticket_creator_id in open_tickets_data:
                del open_tickets_data[ticket_creator_id] 
                save_open_tickets_data(open_tickets_data) 



@bot.tree.command(name="ping-shop", description=f"Pings the role shop ping")
async def pingingRole(interaction: discord.Interaction):
    required_role_id = 1280643425670135849  

   
    unallowed_channel_ids = {
        966584411657232384, 1020130539488952390, 1143357516680531968,
        1276666594780512421, 1217791275433197578, 1217789669605904425,
        995428903948652554, 966608766793547786, 966609121493278752
    }

   
    if interaction.channel.id in unallowed_channel_ids:
        await interaction.response.send_message("This command cannot be used in this channel.", ephemeral=True)
        return

    
    if not interaction.channel.name.startswith("〉"):
        await interaction.response.send_message("This command can only be used in channels starting with '〉'.", ephemeral=True)
        return

   
    if not any(role.id == required_role_id for role in interaction.user.roles):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    
    store_credit = load_store_credit()
    user_id = str(interaction.user.id)

   
    if user_id not in store_credit or store_credit[user_id] <= 0.99:
        await interaction.response.send_message("You don't have enough Store Credit to use this command. DM <@929655970576089128> to buy Store Credit!", ephemeral=True)
        return

 
    store_credit[user_id] -= 1
    save_store_credit(store_credit)

    
    await interaction.response.send_message("Successfully pinged", ephemeral=True)
    await interaction.channel.send(f"<@&973675853462519850>")

@bot.tree.command(name="ping-everyone", description=f"Pings everyone")
async def everyoneping(interaction: discord.Interaction):
    required_role_id = 1280643425670135849 

  
    unallowed_channel_ids = {
        966584411657232384, 1020130539488952390, 1143357516680531968,
        1276666594780512421, 1217791275433197578, 1217789669605904425,
        995428903948652554, 966608766793547786, 966609121493278752
    }

    
    if interaction.channel.id in unallowed_channel_ids:
        await interaction.response.send_message("This command cannot be used in this channel.", ephemeral=True)
        return

 
    if not interaction.channel.name.startswith("〉"):
        await interaction.response.send_message("This command can only be used in channels starting with '〉'.", ephemeral=True)
        return

    
    if not any(role.id == required_role_id for role in interaction.user.roles):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

   
    store_credit = load_store_credit()
    user_id = str(interaction.user.id)

   
    if user_id not in store_credit or store_credit[user_id] <= 2.99:
        await interaction.response.send_message("You don't have enough Store Credit to use this command. DM <@929655970576089128> to buy Store Credit!", ephemeral=True)
        return

    
    store_credit[user_id] -= 3
    save_store_credit(store_credit)

    
    await interaction.response.send_message("Successfully pinged", ephemeral=True)
    await interaction.channel.send("@everyone")

def load_store_credit():
    try:
        with open('StoreCredit.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("Error: The StoreCredit.json file is corrupted.")
        return {}

def save_store_credit(data):
    with open('StoreCredit.json', 'w') as f:
        json.dump(data, f, indent=4)

client.run("Bot token") 
