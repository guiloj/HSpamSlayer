# plugins

### **"plugins"**

> [config.json](./config.md)

```json
"plugins": []
```

List of all the plugin objects that will be called by the plugin manager.

## **plugin object**

```json
{
    "types": [],
    "script": ""
}
```

### **"types"**

List of event types that this plugin listens to.

TYPES

-   `"on_invite"` - Fired when bot receives an invite.
-   `"on_main_critical"` - Fired when [main.py](../../src/main.py) detects that one of the scripts has halted.
-   `"on_remove"` - Fired when the bot is removed from a sub's moderators.
-   _more coming soon_

### **"script"**

The name of the script that will be fired. (must be located in [plugins folder](../../plugins))

## **script file**

-   [plugin base](../../plugins/_plugin_base.py)
-   [example plugin](../../plugins/webhook_plugin.py)

## **built in**

-   [webhook plugin](./plugins_/webhook_plugin.md)
