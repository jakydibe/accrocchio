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


these are some images of the esp32 
![immagine_accrocchio_2](https://user-images.githubusercontent.com/78015812/218266673-0864081e-785f-4ee1-90a7-0b62c24b7f3e.jpeg)
![immagine_accrocchio_1](https://user-images.githubusercontent.com/78015812/218266674-13b1fa03-2cd4-43c4-93af-8ae37dbf7f8a.jpeg)
