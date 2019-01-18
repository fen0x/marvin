import json
import logging
import requests
import praw
import io

from lxml.html import fromstring
from urllib import parse as urlparse, request as urlrequest, error as urlerror
from functools import partial
from bs4 import BeautifulSoup
from telegram import MessageEntity, ChatMember, User, Chat
from telegram.ext import CommandHandler, Filters, Updater

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Logger reference
logger = logging.getLogger(__name__)


class MarvinBot:
    # The subreddit where the bot must post
    subreddit_name = None
    # The authorized group id, used to deny commands from other chats
    authorized_group_id = None
    # The default comment the bod will automatically add to every post submitted
    default_comment_content = None
    # The files to open on startup
    config_file_name = "content/bot_data.json"
    comment_file_name = "content/defaultComment.txt"

    @staticmethod
    def get_page_title_from_url(page_url: str):
        """ Function that return the title of the given web page
        :param page_url: The page to get the title from
        :return: A string that contain the title of the given page
        """
        try:
            soup = BeautifulSoup(urlrequest.urlopen(page_url), "lxml")
        except urlerror.URLError:
            # If an error happens let's download the HTML using requests
            r = requests.get(page_url)
            tree = fromstring(r.content)
            title = tree.findtext('.//title')
            if title is not None:
                return str(title)
            else:
                return None
        return str(soup.title.string)

    @staticmethod
    def is_sender_admin(bot, chat_id: int, user: User):
        """
        Function that return if the given user is an admin in the given chat
        :param bot: The current bot instance
        :param chat_id: The id of the chat
        :param user: The user to check
        :return: True if the user is an admin in the given chat, False otherwise
        """
        user_info = bot.get_chat_member(chat_id, user)
        if user_info.status == ChatMember.ADMINISTRATOR or user_info.status == ChatMember.CREATOR:
            return True
        else:
            return False

    def is_message_in_correct_group(self, chat: Chat):
        """
        Function that return if the message has been sent in the correct group
        :param chat: The chat where the message has been sent
        :return: True if the message is in the group saved in the JSON, False otherwise
        """
        return chat.id == self.authorized_group_id

    def add_default_comment(self, post_submission):
        """
        Function that add the default comment to the given post submission
        :param post_submission: The submitted post where the bot should add the comment
        """
        post_submission.reply(self.default_comment_content)
        logger.info("Default comment sent!")

    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        update.message.reply_text('In un gruppo, rispondi ad un link con il comando /postalink')

    def postalink(self, subreddit, bot, update):
        # Check if the command is used as reply to another message
        if not update.message.reply_to_message:
            update.message.reply_text("Per usare questo comando devi rispondere ad un messaggio")
            return
        # Check if the command has been used in the correct group
        '''if not self.is_message_in_correct_group(update.message.chat):
            update.message.reply_text("Spiacente, questo bot funziona solo nel gruppo autorizzato")
            return
        # Check if the command has been used from an administrator
        if not self.is_sender_admin(bot, update.message.chat.id, update.message.from_user.id):
            update.message.reply_text("Spiacente, non sei un amministratore.")
            return'''
        message = update.message.reply_to_message
        logger.info("Autore del messaggio: %s", message.from_user.name)

        urls_entities = message.parse_entities([MessageEntity.URL])
        print(urls_entities, len(urls_entities))
        if not urls_entities:
            update.message.reply_text("Il messaggio originale deve contenere una URL")
            return
        if len(urls_entities) > 1:
            update.message.reply_text("Il messaggio originale deve contenere una **sola** URL")
            return

        link_to_post = next(iter(urls_entities.values()))
        # Check link schema
        link_parsed = urlparse.urlparse(link_to_post)
        if not link_parsed.scheme:
            link_to_post = 'https://' + link_to_post
        elif link_parsed.scheme not in ['http', 'https']:
            update.message.reply_text("Il messaggio originale deve contenere un link HTTP(S)")
            return
        # Fetch page title
        link_page_title = self.get_page_title_from_url(link_to_post)
        if not link_page_title:
            update.message.reply_text("Non sono riuscito a trovare il titolo della pagina")
            return
        logger.debug("Link title from web: %s", link_page_title)
        # Submit to reddit:
        title = link_page_title + " [From telegram" + update.message.from_user.name + "]"
        submission = subreddit.submit(title, url=link_to_post)
        # Add the default comment
        self.add_default_comment(submission)
        # Send the link to Telegram
        logger.info("Link to created post: %s", str(submission.shortlink))
        update.message.reply_text("Post creato: " + str(submission.shortlink))

    def error_handler(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def main(self):
        """Start the bot."""
        print("Starting bot... Reading login Token...")
        # Read the token from the json
        bot_data_file = None
        try:
            with open(self.config_file_name) as data_file:
                bot_data_file = json.load(data_file)
        except FileNotFoundError:
            print("FATAL ERROR-->" + self.config_file_name + " FILE NOT FOUND, ABORTING...")
            quit(1)
        # Read the default comment data
        try:
            self.default_comment_content = io.open(self.comment_file_name, mode="r", encoding="utf-8").read()
        except FileNotFoundError:
            print("FATAL ERROR-->" + self.comment_file_name + " FILE NOT FOUND, ABORTING...")
            quit(1)
        # reddit login
        reddit = praw.Reddit(**bot_data_file["reddit"])
        # Read subreddit
        self.subreddit_name = bot_data_file["reddit"]["subreddit_name"]
        subreddit = reddit.subreddit(self.subreddit_name)
        # Read authorized group name
        self.authorized_group_id = int(bot_data_file["telegram"]["authorized_group_id"])
        # Subreddit log
        print("Connecting to subreddit:" + str(subreddit.display_name) + " - " + str(subreddit.title))

        # Create the EventHandler and pass it your bot's token.
        print("Starting bot... Logging in...")
        updater = Updater(bot_data_file["telegram"]["login_token"])
        print("Starting bot... Setting handler...")
        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))

        dp.add_handler(CommandHandler("postalink", partial(self.postalink, subreddit), Filters.reply))

        # log all errors
        dp.add_error_handler(self.error_handler)

        # Start the Bot
        updater.start_polling()

        print("Starting bot... Bot ready!")
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


if __name__ == '__main__':
    MarvinBot().main()
