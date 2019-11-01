# Jsons description
List of actions that are in save chat app, based on arrangements made on laboratories.

1. [UU](#markdown-header-1action-uu-update-users-uu)

### 1.Action "UU" - Update users
User sends request with list of nicknames:

```
{
   "action":"UU",
   "ulist":[
      "adrian",
      "marcin",
      "tomek"
   ]
}
```
Server respond with list of clients that matches user request and are online  
Also provides ip, port and secret token of two users :
```
{
   "action":"UU",
   "ulist":[
      {
         "adrian":[
            "127.0.0.1",
            1337,
            "superSecretTocken"
         ]
      },
      {
         "marcin":[
            "127.0.0.1",
            1337,
            "superSecretTocken"
         ]
      },
      {
         "tomek":[
            "127.0.0.1",
            1337,
            "superSecretTocken"
         ]
      }
   ]
}
```

