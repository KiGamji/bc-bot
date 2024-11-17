# /b/egonia communuty's Chat Bot

A bot assisting our Telegram chat.  

Currently supports following commands:

* `/stats` — message statistics per day, week and month.  
Usage: send `/stats` command and control the summary via buttons.
* `/exchange` — gets the current USD/EUR exchange rate against the RUB by default or for the another specified pair.  
Usage: send `/exhange` command with specified currency pair, ex. `/exchange USD EUR`
* `/remind` — sets a reminder. You'll be mentioned by the bot message which will be sent after the time you set.  
Usage: send `/remind` command with specified time and message, ex. `/remind 3h do laundry`
* `/layout` — changes the text layout in a message between English and Russian.  
Usage: reply to the desired message with `/layout` command.

The source code of bot isn't bounded to our chat and can be used in any groups.
