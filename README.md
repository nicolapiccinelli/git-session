# git-session
**git-session** is a Python utility used to alias the standard git command. It provides a easier way to the user session management.
The script creates an external database (managed throught JSON) where a list of users is stored in the following folder `${HOME}/.git-session/users.json`.
Running **git** throught this utility will prevent unwanted commits with the wrong user (can happen in case of shared user session on the same machine).

## Usage
The `git-session.py` adds the following subcommands to existing git commands:

- `--add-user` add a new user to the list of git user profiles. It creates automatically a nickname for each new user, the nickname has the following syntax **name.surname**.
- `--rm-user` remove an existing user from the list of git user profiles.
- `--list-user` print in the terminal the list of the git user profiles.
- `--login` set the local user.name and user.email configuration file to the specified user profile.
- `--logout` clear the existing local **user.name** and **user.email** configuration.

## Examples
Alias the standard **git** command with the **git-session** script (e.g. `alias git='python ${HOME}/git-session.py'`).
For now on, the following examples are assumed to have the alias set up:

### Add new user (`--add-user`)
`$ git --add-user "John Doe<john.doe@email.sh>`
### Remove a user (`--rm-user`)
`$ git --rm-user john.doe`
### Print the users list (`--list-user`)
`$ git --list-user`
### Login an existing user (`--login`)
`$ git --login john.doe`
### Logout (`--logout`)
`$ git --logout`

## Todo
- Add git autocomplete through **git-session**
