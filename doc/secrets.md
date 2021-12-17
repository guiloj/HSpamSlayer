# data/secrets.json

-   Create a new reddit account and go to https://www.reddit.com/prefs/apps/

-   Fill the information:

    ![](https://media.discordapp.net/attachments/766913349442600971/913871795885584424/unknown.png)

    -   Choose `script` on the left.
    -   Name: The app name.
    -   Description: Add a description.
    -   Redirect uri: just add "https://localhost"

-   Click create app:
-   Fill `secrets.json` accordingly:

    ![](https://media.discordapp.net/attachments/766913349442600971/913873219168129054/unknown.png)

    -   Red: "id"
    -   Blue: "secret"

    ```json
    {
        "secret": "",
        "id": ""
    }
    ```

-   Add the username and password for the bot's account:

    ```json
    {
        "username": "",
        "password": ""
    }
    ```

-   Add an agent name **(You can choose whatever name you like)**

    ```json
    {
        "agent": ""
    }
    ```

-   Add a webhook url **(Optional)**

    ```json
    {
        "webhook": ""
    }
    ```
