from telegram.ext import Updater, Handler, CommandHandler, MessageHandler, TypeHandler, Filters, BaseFilter
from telegram import MessageEntity, Message
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def postalink(bot,update):
    update.message.reply_text("Lo posto!")

def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def link(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Hai postato un link!')

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))


    #dp.add_handler(CommandHandler("postalink", postalink, Filters.reply))

    dp.add_handler(CommandHandler(Filters.reply, postalink))


    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))

    # on link echo recon message
    #dp.add_handler(MessageHandler(Filters.entity(MessageEntity.URL), link))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()