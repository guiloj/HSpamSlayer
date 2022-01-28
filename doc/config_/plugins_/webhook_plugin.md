# webhook plugin

_(built for discord webhooks)_

> [config.json](../config.md)

```json
 "plugins": [
    {
        "types": [
            "on_invite",
            "on_main_critical"
        ],
        "script": "webhook_plugin.py"
    }
]
```

---

```json
{
    "webhook": "",
    "messages": {
        "on_invite": {},
        "main_critical": {}
    }
}
```

### **"webhook"**

The **discord** webhook url.

### **"messages"**

```json
"messages": {
    "on_invite": {},
    "main_critical": {}
}
```

**"on_invite"** && **"main_critical"**

The json objects that are posted to the webhook when the bot receives an invite and main detects that a script has halted, respectively. [Read More ...](https://discord.com/developers/docs/resources/webhook#execute-webhook-jsonform-params)

FORMATTING

-   "on_invite"
    -   `%(subreddit)s` - The subreddit that the sent the invite
-   "main_critical"
    -   `%(file_name)s` - The name of the file that failed
    -   `%(exit_code)s` - The exit code of the script that failed
    -   `%(message)s` - What was written in `stderr` by the script
