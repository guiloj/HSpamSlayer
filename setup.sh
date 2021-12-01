#!/bin/sh

mkdir data || echo "mkdir failed! please intervine"
mkdir config || echo "mkdir failed! please intervine"
mkdir cache || echo "mkdir failed! please intervine"

echo "{ \
    \"username\": \"\", \n\
    \"password\": \"\", \n\
    \"secret\": \"\", \n\
    \"id\": \"\", \n\
    \"agent\": \"\", \n\
    \"webhook\": \"\" \n\
}" >> ./data/secrets.json || echo "creating secrets.json failed! please intervine"

echo "{ \
    \"banned_subs\": [] \n\
}" >> ./data/subs.json || echo "creating subs.json failed! please intervine"

echo "{ \n\
    \"webhook\": false, \n\
    \"action\": { \n\
        \"ban_message\": \"\", \n\
        \"ban_reason\": \"\", \n\
        \"duration\": null, \n\
        \"note\": \"\" \n\
    }, \n\
    \"message\": { \n\
        \"subject\":\"\", \n\
        \"message\":\"\" \n\
    } \n\
}" >> ./config/config.json || echo "creating config.json failed! please intervine"

echo "{ \n\
    \"subreddits\": { \n\
    \n\
    } \n\
}" >> ./cache/moderated_subreddits.cache.json || echo "creating moderated_subreddits.cache.json failed! please intervine"

echo "{ \n\
    \"banned_users\": { \n\
    \n\
    } \n\
}" >> ./cache/banned_users.cache.json || echo "creating banned_users.cache.json failed! please intervine"