[![Build Status](https://travis-ci.org/garethpaul/valleybot.svg?branch=master)](https://travis-ci.org/garethpaul/valleybot)

# ValleyBot
<img src="screenshots/logo.png" />

A chatbot based on tech talk.

#### Integrations

Here are some popular chatbot integrations.

**Facebook**

<img src="screenshots/screenshot04.png" width="240" style="width:240px; margin-top:15px" />

**Slack**

<img src="screenshots/screenshot03.png" width="500" style="width:500px; border-radius:4px; margin-top:15px" />

**Web**

<img src="screenshots/screenshot01.png" width="500" style="width:500px; border-radius:4px" />

**Terminal**

<img src="screenshots/screenshot02.png" width="500" style="width:500px; border-radius:4px; margin-top:15px" />

## Settings

Currently we have chatbot integrations for Facebook, Slack, Web and Local Access. The settings file contains more information on settings for these bot channels.


## How to get started ?

#####  1.  Initially clone the repo.

```
git clone https://github.com/garethpaul/valleybot.git
```

#####  2.  Get the requirements for the project

```
pip install -r requirements.txt
```

#####  3. (option 1)  Run the server

```
python ./app.py {port}
```

#####  3. (option 2)  Python

 ```
import bot
bot.respond("Hello there valley bot what's going on?")
 ```

## Running Externally

### AWS Lambda

###### 1. Run through the install process above.
###### 2. Zip up the contents of this project.

```
zip -rf ~/ValleyBot.zip *
```

###### 3. Upload the zip to S3
###### 4. Input your S3 url inside Lambda
###### 4. Point your lambda function to run bot.respond_json
###### 5. You will then get a API URL from Lambda to run the bot.


### Heroku

###### 1. Create a Heroku Instance

```
heroku create

```


###### 2. Push to Heroku

```

git push heroku master
```
