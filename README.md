# accrocchio
This project is a simple sound notifier for cryptocurencies buy/sell signals

made in collaboration with : https://github.com/Luigi31-github

this project is split in 2 parts: -python Restful API on AWS
                                  -ESP-32 sound notifier 

The first part is the python code which is basically a program that calculates some technical indicators (for now it's only vwap and supertrend) and 
gives buy/sell signals based on them. then puts this signals on a restful API using FastAPI and tunnels this API with a permanent ngrok tunnel.
(for curios people it is hosted at: http://c452-13-38-10-190.eu.ngrok.io, please don't DDOS me ahahahaha).
The API is hosted on a free Amazon Web Server.

Then there is the C part which is just the code for an ESP-32 that connects to a wi-fi and using that wifi it connects to my API and from the information it gets it 
decides wether to make a sound notifcation with an active buzzer and also displays the info on a little OLED display.

