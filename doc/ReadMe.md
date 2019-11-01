# Jsons description
List of actions that are in save chat app, based on arrangements made on laboratories:

1. [UU - Update Users](#markdown-header-action-uu-update-users)
2. [L/R - Login/Register](#)
3. [OK](#)
4. [ERROR](#)
5. [HELLO](#)
5. [M - Message](#)
6. [OUT](#)
7. [CT - Connection Token](#)

### Action UU - Update users
User sends request with list of nicknames:

```json
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
```json
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

### Action L/R - Login/Register
User sends login or register data:

```json
{
   "action":"L",
   "login":"misiek36",
   "password":"kochamPiwo",
   "port":1234
}
```
OR
```json
{
   "action":"R",
   "login":"misiek36",
   "password":"kochamPiwo",
   "port":1234
}
```
Server respond with `OK` (logged in) or `ERROR`(some error)
```json
{
   "action":"OK"
}
```
OR
```json
{
   "action":"ERROR",
   "message":"Wrong login data"
}
```

### Action OK
Action is positive response to other action

```json
{
   "action":"OK"
}
```

### Action ERROR
Action is negative response to other action, also providing error message.

```json
{
   "action":"ERROR",
   "message":"Wrong login data"
}
```

### Action HELLO
First action sent after connecting.

```json
{
   "action":"HELLO"
}
```

### Action M - Message
Action which sends message data to other client after establishing connection.

```json
{
   "action":"M",
   "message":"Siema Eniu! ;)"
}
```

### Action M - Message
Disconnect action.

```json
{
   "action":"OUT"
}
```

### Action CT - Connection Token
Action which sends to client to which we are connecting `Connection Token`.
Client after `Connection Token` checks it on server and respond with OK or ERROR.

```json
{
   "action":"CT",
   "nick":"tomek",
   "token":"asgklsghaoghpoiwehatopa"
}
```

