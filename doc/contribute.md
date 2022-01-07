# Contributing rules

-   You must always change a docstring if your changes make them incorrect.
-   You must always add a docstring to any new functions.
-   You must always explain your changes.
-   You must always follow the [google template](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings) for docstrings:

    ```py
    """
    This is an example of Google style.

    Args:
        param1 (type): This is the first param.
        param2 (type): This is a second param.

    Returns:
        type: This is a description of what is returned.

    Raises:
        KeyError: Raises an exception.
    """
    ```

-   You must always respect others.
-   You must always make your functions [statically typed](https://docs.python.org/3/library/typing.html):
    ```py
    def foo(bar: str) -> str:
        """
        Add the string `bar` to the end of the string "foo: " and return it.

        Args:
            bar (str): The string to be appended.

        Returns:
            str: Result of the appended string.

        Example:
        ```py
        >>> foo("bar")
        foo: bar
        ```
        """
        return f'foo: {bar}'
    ```
-   You should try your best to write readable code.
-   You should follow the comment rules on top of the file:

    ```py
    """
        @comments
        '?': why is this code here?
        '*': what is the code doing
        '!': warning!
        'NOTE': a note

        @dev
        'TODO': todo notes
        'FIXME': needs fixing
        'XXX': makes no sense but works
    """
    ```

-   You are invited to add your name to comments like so:
    ```py
    # XXX: (@guiloj) wtf?
    ```
-   You are invited to download these plugins to your vscode install:
    -   [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)
    -   [BetterComments](https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments)
    -   [AutoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)
-   You are invited to use the `black` formatter.
    -   `pip install black`|`pip3 install black`|`python3 -m pip install black`
    -   `black .`
-   You must NOT intentionally break the code.
