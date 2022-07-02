# TODO for v3.1.0

> restarts with every new version

| Priority Markers |         Meaning          |
| :--------------: | :----------------------: |
|   **(URGENT)**   |    very urgent tasks     |
| **(important)**  | important/priority tasks |
|   **(minor)**    |   minor/optional tasks   |

|    Type Markers    |                  Meaning                   |
| :----------------: | :----------------------------------------: |
|   **[feature]**    |               a new feature                |
|     **[fix]**      |       a fix for an existing feature        |
|    **[rework]**    |  a rewrite/rework of an existing feature   |
|     **[idea]**     | an idea that might turn into a new feature |
| **[experimental]** |          an experimental feature           |

---

-   [ ] Add Image recognition **[feature] [experimental]**
    -   [x] Create plugin barebones
    -   [ ] Make the plugin customizable
    -   [x] Properly catch exceptions
    -   [x] Create image blacklist
    -   [ ] Integrate plugin with core
-   [x] Add sub configs **[feature]**
    -   [x] Introduce json validation methods
    -   [x] Create a way for subs to submit config files
    -   [x] Introduce sub configs to the `Configs` helper object
    -   [x] Use sub configs on all scripts
    -   [ ] Make configs properly accessible **(minor)**
-   [ ] Get rid of inconsistency issues with the code **[fix]**
    -   [x] Normalize `Path` usage
    -   [x] Normalize imports with all scripts
    -   [ ] Normalize naming methods for all variables, functions and classes
    -   [ ] Add docstrings to all classes and functions
-   [x] (ACTUALLY) Kill all threads when a critical unexpected error was raised **[fix]**
-   [ ] Update Pipfile and requirements.txt files before pushing to `master`
-   [ ] Test new features and fixes **(important)**
-   [x] Get rid of all nullable function results with the rust approach. [\_rust_types.py](src/_rust_types.py)
-   [ ] Use `.expect()` with more helpful messages.
-   [ ] Implement in-code caches for all file helper methods to avoid unnecessary memory allocations.
-   [ ] Fix the local config schema **[fix]**
