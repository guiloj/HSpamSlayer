# config/config.json

## "webhooks"

`"use"`

Decides if webhooks are going to be used by the script, if it is ever set to `true` a webhook must be added to [secrets.json](https://github.com/guiloj/HSpamSlayer/blob/master/doc/secrets.md) and the following objects must be configured.

`"main_critical"`

The json object that is posted to the webhook when a script fails and halts. The formatting strings that can be added are:

-   `"%(filename)s"` - The file name of the script that failed.
-   `"%(exitcode)s"` - The exit code that the script returned.
-   `"%(error)s"` - The error message.

`"invite_accept"`

The json object that is posted to the webhook when an invite gets accepted. The formatting strings that can be added are:

-   `"%(sub)s"` - The subreddit that has invited the bot.

```json
{
    "webhooks": {
        "use": false,
        "main_critical": {},
        "invite_accept": {}
    }
```

---

## "no_invite"

list of subs that the bot should not accept invites from (besides blacklisted subs).

```json
    "no_invite": [],
```

---

## "action"

`"ban_message"`

The message that is sent via modmail to a user that got banned by the bot.

`"ban_reason"`

The reason for the ban.

`"duration"`

For how long the ban lasts (in days), `null` = perma ban.

`"note"`

The mod's note, shown in the mod log.

**[read more...](https://www.reddit.com/dev/api/#POST_api_friend)**

```json
    "action": {
        "ban_message": "",
        "ban_reason": "",
        "duration": null,
        "note": ""
    }
```

---

## "message"

`"subject"`

The subject of the modmail being sent to a sub's mods on invite accept.

`"message"`

The content of the modmail being sent on invite accept. The message accepts the following formatting strings:

-   `"{0}"` - The sub that invited the bot.

```json
    "message": {
        "subject": "",
        "message": ""
    }
```

---

## "announcement"

`"title"`

The title of the announcement being posted on a sub on invite, **if there are less then 2 pinned posts on that sub**.

`"selftext"`

The content of the announcement being posted on a sub on invite.

```json
    "announcement": {
        "title": "",
        "selftext": ""
    }
```

---

## "remove"

`"message"`

The message being sent to a user on post removal.

`"type"`

What type of message is being sent, defaulted to `"public"` meaning a sticky comment on the post in question.

**[read more...](https://praw.readthedocs.io/en/stable/code_overview/other/submissionmoderation.html#praw.models.reddit.submission.SubmissionModeration.send_removal_message)**

```json
    "remove": {
        "message": "",
        "type": "public"
    }
}
```

---

When you are done configuring a the bot it should look a little something like this:

```json
{
    "webhooks": {
        "use": false,
        "main_critical": {},
        "invite_accept": {}
    },
    "no_invite": ["Subs", "that", "you", "don't", "want", "invites", "from"],
    "action": {
        "ban_message": "Message sent when a user is banned",
        "ban_reason": "The reason why he was banned",
        "duration": null,
        "note": "The mod note"
    },
    "message": {
        "subject": "Subject of the message sent to a sub on invite accept",
        "message": "The message sent to a sub on invite accept, add {0} where you want the name of the sub to be"
    },
    "announcement": {
        "title": "Title of the announcement that is posted to a sub on invite accept if there are slots available",
        "selftext": "Content of the announcement"
    },
    "remove": {
        "message": "The message that is sent when a user get's a post removed",
        "type": "public"
    }
}
```
