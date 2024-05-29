# EIMIS experimentation whitelist Synapse module

![Matrix](https://img.shields.io/badge/matrix-000000?logo=Matrix&logoColor=white)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/eimis-ans/white-list-synapse-module/lint.yml?label=lint&logo=github)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/eimis-ans/white-list-synapse-module/test.yml?label=test&logo=github)
![License](https://img.shields.io/badge/license-Apache%202-blue.svg)

## Use case

Let's say you run an experiment in which you operate a Matrix server. An external ID provider is configured but you want to allow only specific users to join the experiment. You also want an easy way to manage a user whitelist.

## Whitelist module

To do so, this repo contains a Synapse Module that will use `check_registration_for_spam` hook. It will allow users based on their mention in a specific whitelist room 🤓

## Try it out

### some /etc/hosts entries

```bash
echo "127.0.0.1 idp.local" | sudo tee -a /etc/hosts
echo "127.0.0.1 matrix.local" | sudo tee -a /etc/hosts
```

### Run the stack

```bash
docker compose up -d
```

### Create users

Create a _whitelist-manager_ and _beta-tester_ user

- Go to <http://idp.local:8443>
- login with admin /admin
- select `local` realm
- users / `Add a user`
- fill at least Username and save
- go to `Credentials` tab and set a password

### Create white list

- Go to <http://localhost:1983>
- Login with _whitelist-manager_ user
- Create an **unencrypted** room called Whitelist
- Write a message containing some random user id
- Get the room ID
- edit `docker-test-config/mx-conf/homeserver.yaml`
- fill this part:
  
  ```yaml
    module: white_list_module.EimisWhiteList
    config:
      room_id: ROOM_IDs
  ```

### Try to join

- Open an other browser session
- Go to <http://localhost:1983>
- Try login with _beta-tester_ user, you'll be denied
- Go back to the whitelist room
- edit your message or write a new message containing _beta-tester_ username
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

### run locally

```bash
docker compose watch
```

(Any change in the module or the conf will restart Synapse container)
