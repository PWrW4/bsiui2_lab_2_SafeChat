# Jsons description
List of actions that are in save chat app, based on arrangements made on laboratories:

1. [UU - Update Users](#markdown-header-action-uu-update-users)
2. [L/R - Login/Register](#markdown-header-action-lr-loginregister)
3. [OK](#markdown-header-action-ok)
4. [ERROR](#markdown-header-action-error)
5. [HELLO](#markdown-header-action-hello)
5. [M - Message](#markdown-header-action-m-message)
6. [OUT](#markdown-header-action-out)
7. [CT - Connection Token](#markdown-header-action-ct-connection-token)

---

## Action UU - Update users
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
[BACK TO TOP](#markdown-header-jsons-description)

---

## Action L/R - Login/Register
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
Server respond with [OK](#markdown-header-action-ok) (logged in) or [ERROR](#markdown-header-action-error) (some error)
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
[BACK TO TOP](#markdown-header-jsons-description)

---


## Action OK
Action is positive response to other action

```json
{
   "action":"OK"
}
```

[BACK TO TOP](#markdown-header-jsons-description)

---

## Action ERROR
Action is negative response to other action, also providing error message.

```json
{
   "action":"ERROR",
   "message":"Wrong login data"
}
```

[BACK TO TOP](#markdown-header-jsons-description)

---

## Action HELLO
First action sent after connecting.

```json
{
   "action":"HELLO"
}
```

[BACK TO TOP](#markdown-header-jsons-description)

---

## Action M - Message
Action which sends message data to other client after establishing connection.

```json
{
   "action":"M",
   "message":"Siema Eniu! ;)"
}
```

[BACK TO TOP](#markdown-header-jsons-description)

---

## Action OUT
Disconnect action.

```json
{
   "action":"OUT"
}
```

[BACK TO TOP](#markdown-header-jsons-description)

---

## Action CT - Connection Token
Action which sends to client to which we are connecting `Connection Token`.

```json
{
   "action":"CT",
   "nick":"tomek",
   "token":"asgklsghaoghpoiwehatopa"
}
```

Client after `Connection Token` checks it on server and respond with [OK](#markdown-header-action-ok) or [ERROR](#markdown-header-action-error) message and
then disconnects.
```json
{
   "action":"OK"
}
```
OR
```json
{
   "action":"ERROR",
   "message":"Wrong Token"
}
```

[BACK TO TOP](#markdown-header-jsons-description)

---
