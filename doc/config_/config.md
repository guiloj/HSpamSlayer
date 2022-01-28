# config

## config/config.json

```json
{
    "logging": {
        "file_level": 20,
        "stdout_level": 10
    },
    "threading": {
        "max_subs_per_thread": 10
    },
    "on_invite": {
        "send_message": true,
        "message_content": {
            "subject": "",
            "message": ""
        },
        "make_announcement": false,
        "announcement_content": {
            "title": "",
            "selftext": ""
        },
        "ignore": []
    },
    "on_bad_post": {
        "remove": true,
        "remove_opts": {
            "spam": true
        },
        "remove_message_content": {
            "message": "",
            "type": "public"
        },
        "ban": true,
        "ban_opts": {
            "ban_message": "",
            "ban_reason": "",
            "duration": null,
            "note": ""
        }
    },
    "main.py": {
        "scripts": ["inbox.py", "submissions.py"]
    },
    "plugins": []
}
```

---

### **"logging"**

```json
"logging": {
    "file_level": 20,
    "stdout_level": 10
}
```

**"file_level"**

The level of logging for the file handler

**"stdout_level"**

The level of logging for the stdout handler

[**LEVELS**](https://docs.python.org/3/library/logging.html#levels)

-   `0` - NOTSET
-   `10` - DEBUG
-   `20` - INFO
-   `30` - WARNING
-   `40` - ERROR
-   `50` - CRITICAL

---

### **"threading"**

```json
"threading": {
    "max_subs_per_thread": 10
}
```

**"max_subs_per_thread"**

The maximum amount of subreddits per thread created.

---

### **"on_invite"**

```json
"on_invite": {
    "send_message": true,
    "message_content": {
        "subject": "",
        "message": ""
    },
    "make_announcement": false,
    "announcement_content": {
        "title": "",
        "selftext": ""
    },
    "ignore": []
}
```

**"send_message"**

If a message should be sent via modmail to the subreddit that invited the bot

**"message_content"**

The content of the message. [Read More ...](https://praw.readthedocs.io/en/stable/code_overview/models/subreddit.html?highlight=Subreddit.message#praw.models.Subreddit.message)

FORMATTING

-   "message"
    -   `%(subreddit)s` - The name of the subreddit that invited the bot

**"make_announcement"**

If an announcement should be made in the subreddit that invited the bot (not made if the sticky pool is full)

**"announcement_content"**

The content of the announcement. [Read More ...](https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html#praw.models.Subreddit.submit)

**"ignore"**

List of subreddits that will get their invites ignored. (blacklist already included)

---

### **"on_bad_post"**

```json
"on_bad_post": {
    "remove": true,
    "remove_opts": {
        "spam": true
    },
    "remove_message_content": {
        "message": "",
        "type": "public"
    },
    "ban": true,
    "ban_opts": {
        "ban_message": "",
        "ban_reason": "",
        "duration": null,
        "note": ""
    }
}
```

**"remove"**

If a crosspost from a blacklisted sub should be removed when detected.

**"remove_opts"**

The options for how the post should be removed. [Read More ...](https://praw.readthedocs.io/en/stable/code_overview/other/submissionmoderation.html#praw.models.reddit.submission.SubmissionModeration.remove)

**"remove_message_content"**

Content and options for the removal message. [Read More ...](https://praw.readthedocs.io/en/stable/code_overview/other/submissionmoderation.html#praw.models.reddit.submission.SubmissionModeration.send_removal_message)

**"ban"**

If the author of the crosspost from a blacklisted sub should be banned.

**"ban_opts"**

The options for how the user should be banned.

-   Read More ...

    -   [SubredditRelationship.add](https://praw.readthedocs.io/en/stable/code_overview/other/subredditrelationship.html#praw.models.reddit.subreddit.SubredditRelationship.add)
    -   [banned.add](https://praw.readthedocs.io/en/stable/code_overview/models/subreddit.html?highlight=banned.add#praw.models.Subreddit.banned)
    -   [POST_api_friend](https://www.reddit.com/dev/api/#POST_api_friend) (comprehensive)
    -   [redditdev](https://www.reddit.com/r/redditdev/comments/6vlvfb/comment/dm1i9a4/) (human readable) - **Recommended**

---

### **"main.py"**

```json
"main.py": {
    "scripts": ["inbox.py", "submissions.py"]
}
```

**"scripts"**

The list of scripts that will be called by [main.py](../../src/main.py), (all of those that start with `_` will be ignored)

---

### **"plugins"**

```json
"plugins": []
```

## [Configure plugins...](./plugins.md)
