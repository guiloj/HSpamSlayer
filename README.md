# HSpamSlayer

<a href="https://www.pixiv.net/en/artworks/59561246"><img style="height: 400px; border-radius: 10px;" class="taiga" src="https://cdn.discordapp.com/attachments/766913349442600971/913633329130115092/59561246_p0_master1200.png"><img></a>

A simple bot to help keep spam away from your _H_ subreddit.

# Table of contents

-   [[About](#about)] - Information about the bot
-   [[Setup](#setup)] - Invite the bot to mod your subreddit
-   [[Installation](#installation)] - Install and modify your version of the bot ([GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.txt))
-   [[Docs](https://github.com/guiloj/HSpamSlayer/tree/master/doc/)] - **RTFM!**

# About

HSpamSlayer is a bot that is programmed to stream posts from blacklisted subreddits and ban the author in every subreddit it moderates.

It was made to handle the current crosspost spam in many subreddits where a bot would get a random post from sub _A_ and submit it to its own subreddit with the same title and then crosspost it back to sub _A_.

To stop this HSpamSlayer has a blacklist of carefully selected subreddits to ban authors from, if you want to make a suggestion you can! just head to [the issues tab](https://github.com/guiloj/HSpamSlayer/issues) and select subreddit proposal when creating a new issue.

# Setup

> If you just want the default bot

-   Invite https://www.reddit.com/user/HSpamSlayer to be a mod on your sub!
-   Wait about 2 minutes for the bot to accept the invite
-   Make sure the bot has the `Manage Users` permission, otherwise the bot will not be able to work properly
-   Sit down and enjoy the free spam firewall

# Installation

> If you want to run the bot and change the configurations for yourself

---

## Warning

**If you fork or clone this project you MUST make any changes public and include the [GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)) in your repository.**

![asd](https://www.gnu.org/graphics/gplv3-with-text-136x68.png)

_(configuration changes are not changes)_

| 🟢 Permissions |        🔵 Conditions         | 🔴 Limitations |
| :------------: | :--------------------------: | :------------: |
| Commercial use |       Disclose source        |   Liability    |
|  Distribution  | License and copyright notice |    Warranty    |
|  Modification  |         Same license         |                |
|   Patent use   |        State changes         |                |
|  Private use   |                              |                |

---

-   Clone this repository
    ```sh
    git clone https://github.com/guiloj/HSpamSlayer.git
    ```
-   Change directory

    ```sh
    cd HSpamSlayer
    ```

-   Create core config directories and files
    ```sh
    mkdir data && mkdir config
    ```
    ```sh
    echo "{ \
        \"username\": \"\", \n\
        \"password\": \"\", \n\
        \"secret\": \"\", \n\
        \"id\": \"\", \n\
        \"agent\": \"\", \n\
        \"webhook\": \"\" \n\
    }" >> ./data/secrets.json
    ```
    ```sh
    echo "{ \
        \"banned_subs\": [] \n\
    }" >> ./data/subs.json
    ```
    ```sh
    echo "{ \n\
        \"webhook\": false, \n\
        \"action\": { \n\
            \"ban_message\": \"\", \n\
            \"ban_reason\": \"\", \n\
            \"duration\": null, \n\
            \"note\": \"\" \n\
        }, \n\
        \"message\": { \n\
            \"subject\":\"\", \n\
            \"message\":\"\" \n\
        } \n\
    }" >> ./config/config.json
    ```
-   Configure the bot
    -   [Configure the config file -> ./config/config.json](https://github.com/guiloj/HSpamSlayer/blob/master/doc/config.md)
    -   [Configure the secrets file -> ./data/secrets.json](https://github.com/guiloj/HSpamSlayer/blob/master/doc/secrets.md)
    -   [Configure the subs file -> ./data/subs.json](https://github.com/guiloj/HSpamSlayer/blob/master/doc/subs.md)
