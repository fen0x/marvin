import json
import logging
from urllib import parse as urlparse, request as urlrequest, error as urlerror
from functools import partial

import praw
from bs4 import BeautifulSoup
from telegram import MessageEntity
from telegram.ext import CommandHandler, Filters, Updater

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Logger reference
logger = logging.getLogger(__name__)


def get_page_title_from_url(page_url: str):
    """ Function that return the title of the given web page
    :param page_url: The page to get the title from
    :return: A string that contain the title of the given page
    """
    try:
        soup = BeautifulSoup(urlrequest.urlopen(page_url), "lxml")
    except urlerror.URLError:
        return None
    return str(soup.title.string)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('In un gruppo, rispondi ad un link con il comando /postalink')


def postalink(subreddit, bot, update):
    # print("Reply from:" + str(update.message.reply_to_message.text))
    if not update.message.reply_to_message:
        update.message.reply_text("Per usare questo comando devi rispondere ad un messaggio")
        return
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
    logger.debug("Link in message: %s", link_to_post)
    # Check link schema
    link_parsed = urlparse.urlparse(link_to_post)
    if not link_parsed.scheme:
        link_to_post = 'https://' + link_to_post
    elif link_parsed.scheme not in ['http', 'https']:
        update.message.reply_text("Il messaggio originale deve contenere un link HTTP(S)")
        return
    # Fetch page title
    link_page_title = get_page_title_from_url(link_to_post)
    if not link_page_title:
        update.message.reply_text("Non sono riuscito a trovare il titolo della pagina")
        return
    logger.debug("Link title from web: %s", link_page_title)
    # Submit to reddit:
    title = link_page_title + " [From telegram" + update.message.from_user.name + "]"
    submission = subreddit.submit(title, url=link_to_post)
    logger.info("Link to created post: %s", str(submission.shortlink))
    update.message.reply_text("Post creato: " + str(submission.shortlink))


def error_handler(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    print("Starting bot... Reading login Token...")
    # Read the token from the json
    file_name = "bot_data.json"
    bot_data_file = None
    try:
        with open(file_name) as data_file:
            bot_data_file = json.load(data_file)
    except FileNotFoundError:
        print("FATAL ERROR-->" + file_name + " FILE NOT FOUND, ABORTING...")
        quit(1)

    # reddit login
    reddit = praw.Reddit(**bot_data_file["reddit"])
    print("Bot username:" + str(reddit.user.me()))
    # Read subreddit
    subreddit = reddit.subreddit(bot_data_file["reddit"]["subreddit_name"])
    # Subreddit test - TODO remove this
    print(subreddit.display_name)
    print(subreddit.title)

    # Create the EventHandler and pass it your bot's token.
    print("Starting bot... Logging in...")
    updater = Updater(bot_data_file["telegram"]["login_token"])
    print("Starting bot... Setting handler...")
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("postalink", partial(postalink, subreddit), Filters.reply))

    # log all errors
    dp.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    print("Starting bot... Bot ready!")
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
