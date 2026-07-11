# This example requires the 'message_content' intent.

import discord, os, json, requests
import LeagueData
from dotenv import load_dotenv

load_dotenv(override=False)

data = LeagueData.LeagueData()

bot_token = os.getenv("BOT_TOKEN")
application_id = os.getenv("APPLICATION_ID")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')


class setupButtons(discord.ui.View):

    def __init__(self, timeout):
        super().__init__(timeout=timeout)

    def load_other_buttons(self):

        @discord.ui.button()
        async def load_button(self):
            pass
        
        # create option to select favourite champ (the one that appears on the widget) from dropdown ----------------------------------
            # if not possible via dropdown or button, make update fave champ command instead

@tree.command(
    name="setup",
    description="setup bot with your gamename and tagline"
)
async def setup(ctx, gamename:str, tagline:str):
    
    view = setupButtons(timeout=180)
    view.add_item(discord.ui.Button(
        label = "Authorize", 
        style = discord.ButtonStyle.link,
        url = "https://discord.com/oauth2/authorize?client_id=1522907002110742678&response_type=code&redirect_uri=https%3A%2F%2Fdiscord.com&scope=connections+openid+sdk.social_layer"
    ))
    
    view.load_other_buttons() # load other buttons after auth button

    # add button item to view to link app to riot account 
        # preventing impersonation from just reading an input gamename#tagline
        # needs RSO (riot sign on) access ------------------------------------------
        # needs discord connection access (currently unsupported via discord api: https://github.com/discord/discord-api-docs/discussions/8430)

    # create database that takes gamename, tagline and output from LeagueData class ----------------------------------

    await ctx.response.send_message("Please authorize the bot!", view=view)

@tree.command(
    name="refresh",
    description="reload the widget on your profile. use after having changed any of the fields",
)
async def refresh(ctx):
    
    # create payload/content using json
        # skip the username field?
            # username field corresponds to making an application identity, relevant only for a self-made widget (?)

        # our python patch function takes key value pairs, just parse json
    user_json = None
    with open("info.json") as json_data:
        user_json = json.load(json_data)
    
    # specify url
    patch_url = f"https://discord.com/api/v9/applications/{application_id}/users/{ctx.user.id}/identities/0/profile"

    # create httpclient
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bot {bot_token}'
    }
    
    print(type(user_json))
    # use httpclient to patchasync
    try:
        response = requests.patch(url=patch_url, json=user_json, headers=header)
        match response.status_code:
            case 201:
                await ctx.response.send_message("Newly added")
            case 204:
                await ctx.response.send_message("Already added")
            case _:
                print(f"Error: response code {response.status_code} {response.content}")
            
    except Exception as e:
        print(f"Error: failed to refresh {repr(e)}")


async def clear(): # clear user's entry in db
    pass


# also let them manually change stuff:

    # fields in widget:
        # ez
            # 1. highest mastery champ
            # 2. total mastery (another api call)

        # idk yet (check playlist)
            # 3. total play time
            # 4. 
            # 5. ranked rank
            # 6. ranked flex rank

client.run(bot_token)
