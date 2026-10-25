# Whitelist Synapse module

![Matrix](https://img.shields.io/badge/matrix-000000?logo=Matrix&logoColor=white)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ad2ien/white-list-synapse-module/lint.yml?label=lint&logo=github)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ad2ien/white-list-synapse-module/test.yml?label=test&logo=github)
![License](https://img.shields.io/badge/license-Apache%202-blue.svg)

## Use case

Let's say you run an experiment in which you operate a Matrix server. An external ID provider is configured but you want to allow only specific users to join the experiment. You also want an easy way to manage a user whitelist.

## Whitelist module

To do so, this repo contains a Synapse Module that will use `check_registration_for_spam` hook. It will allow users based on their mention in a specific whitelist room 🤓

## Try it out

### Run the stack

```bash
docker compose up -d
```

- Keycloak (admin + IdP): <http://localhost:8080>
- Synapse: <http://localhost:8008>
- Element: <http://localhost:1983>

### Create users

Create a _whitelist-manager_ and _beta-tester_ user

- Go to <http://localhost:8080>
- login with admin / admin
- select `local` realm
- users / `Add a user`
- fill at least Username and save
- go to `Credentials` tab and set a password

### Create white list

- Go to <http://localhost:1983>
- Login with _whitelist-manager_ user (via Keycloak SSO)
- Create an **unencrypted** room called Whitelist
- Write a message containing some random user id
- Get the room ID
- edit `docker-test-config/mx-conf/homeserver.yaml`
- set `room_id` to the ID you just copied, then restart Synapse
  (`docker compose restart synapse`):
  
  ```yaml
    module: white_list_module.EasyWhiteList
    config:
      room_id: ROOM_IDs
  ```

> If the module's `room_id` is empty the everyone is allowed. If `room_id` points to a room that doesn't exist yet, every registration is denied.

### Try to join

- Open another browser session (or incognito)
- Go to <http://localhost:1983>
- Try to login with _beta-tester_ user via Keycloak SSO, you'll be denied
- Go back to the whitelist room (as _whitelist-manager_)
- edit your message or write a new message containing the _beta-tester_ username
- Go back to the login (as _beta-tester_) and try again
- -> You should be accepted 🎉

## Dev

### lint

```bash
tox -e check_codestyle
```

### test

```bash
tox -e py
```
