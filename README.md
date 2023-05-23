# Pcote's OSRS Discord Bot
**A Discord bot with some OSRS utilities.**

## Features

**Display on a Discord channel a KC leaderboard from a WOM group.**
* Top 1 leaderboard
![Top1.png](./images/Top1.png)
* Top X leaderboard
![Top3.png](./images/Top3.png)


## Installation
[Install Python](https://www.python.org/downloads/)

Install PIP
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
del ./get-pip.py
```

Install the necessary packages 
```
pip install discord
pip install requests
```

## Configuration

A **secrets.json** file should be created in the root folder with the following content filled properly.
```JSON
{
    "BOT_TOKEN": "",
    "WOM_API_KEY": "",
    "WOM_GROUP": 1234,
    "UPDATE_HS_EVERY_X_MIN": 30,
    "HS_CHANNEL_ID": 123456789,
    "TOP_X": 3
}
```

## Execution

Simply run this command from the root directory.
```
python main.py
```