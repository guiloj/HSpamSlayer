# config/config.json

## "webhook"

**Why:** If anything goes wrong with `mod_posts.py` or `accept_invites.py` the `_stdmodule.send_to_webhook` function that is called in `main.py` is made to alert the user that something went wrong with scripts and that action must be taken.

**Type:** Boolean

**Example:**

> config.json

```json
{
    "webhook": true
}
```

> secrets.json

```json
{
    "webhook": "https://discord.com/api/webhooks/000000000000000000/00000000000000000000000000000000000000000000000000000000000000000000"
}
```

**Warnings:**

-   Made for a discord webhook.
-   Must add the webhook link to the [`../data/secrets.json`](https://github.com/guiloj/HSpamSlayer/blob/master/doc/secrets.md) file

## "action"

**Type:** Dictionary<String, String|Integer>

**What:** The ban configuration container.

### "ban_message"

**Type:** String

**What:** A message that gets sent to a user when it gets banned by the bot.

**Extra:** Add a `{0}` where you want the name of the subreddit to be.

**Example:**

```json
{
    "action": {
        "ban_message": "Sorry for the ban from {0} lmao."
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
    "action": {
        "ban_reason": "spammer"
    }
}
```

### "duration"

**Type:** Integer

**What:** The time a user should be banned for in days, goes from 1 to 999, `null` = permaban.

**Example:**

> One day ban.

```json
{
    "action": {
        "duration": 1
    }
}
```

> Permaban.

```json
{
    "action": {
        "duration": null
    }
}
```

### "note"

**Type:** String

**What:** A note for the actual moderators.

**Example:**

```json
{
    "action": {
        "note": "User is not, in fact, cool."
    }
}
```

## "message"

**Type:** Dictionary<String, String>

**What:** The invite accept message config container.

### "subject"

**Type:** String

**What:** The message subject.

**Example:**

```json
{
    "message": {
        "subject": "Invite Accepted!"
    }
}
```

### "message"

**Type:** String

**What:** The message that is going to be sent to a mod that invited the bot.

**Extra:** Add a `{0}` where you want the name of the subreddit to be.

**Example:**

```json
{
    "message": {
        "message": "We accepted your invite to moderate {0}, enjoy!"
    }
}
```

## "remove"

**Type:** Dictionary<String, String>

**What:** The remove post config container.

### "message"

**Type:** String

**What:** The message sent to the user.

**Example:**

```json
{
    "remove": {
        "message": "got your post removed lmao"
    }
}
```

### "type"

**Type:** String

**What:** The type of remove that should be done.

**Example:**

```json
{
    "remove": {
        "type": "public"
    }
}
```

### [read more...](https://praw.readthedocs.io/en/stable/code_overview/other/submissionmoderation.html#praw.models.reddit.submission.SubmissionModeration.send_removal_message)
