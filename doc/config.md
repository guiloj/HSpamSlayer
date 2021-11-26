# config/config.json

```json
{
    "webhook": null,

    "action": {
        "ban_message": null,
        "ban_reason": null,
        "duration": null,
        "note": null
    }
}
```

## "webhook"

**Why:** If anything goes wrong with `mod_posts.py` or `accept_invites.py` the `_stdmodule.send_to_webhook` function that is called in `main.py` is made to alert the user that something went wrong with scripts and that action must be taken.

**Type:** Boolean

**Example:**

> config.json

```json
{
    "webhook": true,
    ...
}
```

> secrets.json

```json
{
    ...
    "webhook": "https://discord.com/api/webhooks/000000000000000000/00000000000000000000000000000000000000000000000000000000000000000000"
}
```

**Warnings:**

-   Made for a discord webhook.
-   Must add the webhook link to the [`../data/secrets.json`](https://github.com/guiloj/HSpamSlayer/blob/main/doc/secrets.md) file

## "action"

**Type:** Dictionary

**What:** The ban configuration container

### "ban_message"

**Type:** String

**What:** A message that gets sent to a user when it gets banned by the bot.

**Extra:** Add a `{}` where you want the name of the subreddit to be.

**Example:**

```json
{
    ...
    "action":{
        "ban_message": "Sorry for the ban from {} lmao.",
        ...
    }
}
```

"

### "ban_reason"

**Type:** String

**What:** Reason why the user was banned.

**Example:**

```json
{
    ...
    "action":{
        ...
        "ban_reason":"spammer",
        ...
    }
}
```

### "duration"

**Type:** Integer

**What:** The time a user should be banned for in days, goes from 1 to 999, `null` = permaban

**Example:**

> One day ban.

```json
{
    ...
    "action":{
        ...
        "duration": 1,
        ...
    }
}
```

> Permaban.

```json
{
    ...
    "action":{
        ...
        "duration": null,
        ...
    }
}
```

### "note"

**Type:** String

**What:** A note for the actual moderators.

**Example:**

```json
{
    ...
    "action":{
        ...
        "note": "User is not, in fact, cool."
    }
}
```
