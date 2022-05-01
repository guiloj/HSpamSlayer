# HSpamSlayer

[![python v3.8](https://img.shields.io/github/pipenv/locked/python-version/guiloj/HSpamSlayer?style=for-the-badge)](https://www.python.org/downloads/)
[![license GPL-3.0](https://img.shields.io/github/license/guiloj/HSpamSlayer?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0.txt)

[![dependencies](https://img.shields.io/librariesio/github/guiloj/HSpamSlayer?style=for-the-badge)](https://libraries.io/github/guiloj/HSpamSlayer)

[![praw v7.5.0](https://img.shields.io/github/pipenv/locked/dependency-version/guiloj/HSpamSlayer/praw?style=for-the-badge)](https://pypi.org/project/praw/)
[![prawcore v2.3.0](https://img.shields.io/github/pipenv/locked/dependency-version/guiloj/HSpamSlayer/prawcore?style=for-the-badge)](https://pypi.org/project/prawcore/)
[![requests v2.22.0](https://img.shields.io/github/pipenv/locked/dependency-version/guiloj/HSpamSlayer/requests?style=for-the-badge)](https://pypi.org/project/requests/)

<a href="https://www.pixiv.net/en/artworks/59561246"><img style="height: 400px; border-radius: 10px;" class="taiga" src="https://cdn.discordapp.com/attachments/766913349442600971/913633329130115092/59561246_p0_master1200.png"><img></a>

A simple bot to help keep spam away from your _H_ subreddit.

# Table of contents

-   [[About](#about)] - Information about the bot
-   [[Setup](#setup)] - Invite the bot to mod your subreddit
-   [[Installation](#installation)] - Install and modify your version of the bot ([GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.txt))
-   [[Docs](./doc/)] - **RTFM!**
-   [[TODO](./TODO.md)] - Todo list for new features

# About

HSpamSlayer is a bot that is programmed to stream posts from modded subreddits and ban the author of a crosspost that comes from a blacklisted subreddit in every subreddit it moderates.

It was made to handle the current crosspost spam in many subreddits where a bot would get a random post from sub _A_ and submit it to its own subreddit with the same title and then crosspost it back to sub _A_.

To stop this HSpamSlayer has a blacklist of carefully selected subreddits to ban authors from, if you want to make a suggestion you can! just head to [the issues tab](https://github.com/guiloj/HSpamSlayer/issues) and select subreddit proposal when creating a new issue.

# Setup

> If you just want the default bot

-   Invite https://www.reddit.com/user/HSpamSlayer to be a mod on your sub!
-   Wait about 2 minutes for the bot to accept the invite
-   Make sure the bot has the `Manage Users`, `Manage Posts & Comments` and `Manage Mod Mail` permissions, otherwise the bot will not be able to work properly
-   Also check if AutoMod is not deleting these posts automatically, if it is the bot would not work on your sub
-   Sit down and enjoy the free spam firewall

## IMPORTANT

-   The bot will be making a pinned announcement on your subreddit once the invite is accepted. If you don't like this you can remove the post as soon as it's posted, the bot will still work on your sub.

-   You would need to accept that the bot's maintainers would modify the bot without making specific announcements. This is so that the bot can timely respond to spammers by updating its filters without having to run sub-specific versions. If you would like to become a bot maintainer and have a say on the bot's operation, please join our [Discord server](https://discord.gg/GCCPARFf5r).

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
    python3 setup.py
    ```

## [>> Configure the bot](./doc/index.md)
