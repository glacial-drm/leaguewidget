# This example requires the 'message_content' intent.

import discord, os
import LeagueData
from dotenv import load_dotenv

load_dotenv(override=False)

data = None

bot_token = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


class setupButtons(discord.ui.view):

    def __init__(self, timeout):
        super().__init__(timeout=timeout)

    def load_other_buttons():

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
    view.add_item(discord.ui.button(
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
    data = LeagueData.LeagueData(gamename, tagline)

    await ctx.response.send_message("Please authorize the bot!", view=view)

@tree.command(
    name="refresh",
    description="refresh the widget on your profile "
)
async def refresh():
    
    # create payload
        # skip the username field?
    # create content using json
    # specify url
    # create httpclient
    # use httpclient to patchasync
    patch_url = f"https://discord.com/api/v9/applications/{discordApplicationId}/users/{discordUserId}/identities/{identityId}/profile"
    pass

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
