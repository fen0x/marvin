# marvin

Questo bot pubblica tutti i link postati sul gruppo Telegram ItalyInformatica (https://t.me/ItalyInformatica) sul subreddit a cui fa riferimento (https://www.reddit.com/r/ItalyInformatica/).

Il bot deve:

* su comando `/postlink`, in risposta ad un messaggio contenente un link, postare tale link sul subreddit, indicando il nick Telegram dell'autore;
* su comando `/posttext`, in risposta ad un messaggio testuale, postare tale contenuto sul subreddit con il titolo fornito, indicando il nick Telegram dell'autore;
* su comando `/comment`, in risposta ad un messaggio contenente un link ad un post di Reddit (solo se del subreddit ItalyInformatica), aggiungere un commento al post;
* su comando `/delrule`, in risposta ad un messaggio contenente un link ad un post di Reddit (solo se del subreddit ItalyInformatica), cancellare tale post per violazione della regola fornita.

Wiki completa delle funzionalità: https://old.reddit.com/r/ItalyInformatica/wiki/bot
