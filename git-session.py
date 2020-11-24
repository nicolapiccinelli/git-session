#!/usr/bin/python
import sys
import os
import argparse
import json
from json import JSONEncoder, JSONDecoder


class User:
    def __init__(self, name, surname, address):
        self.name = name
        self.surname = surname
        self.address = address
        self.nickname = name.lower() + "." + surname.replace(" ", "").lower()
        self.id = name.lower() + surname.replace(" ", "").lower() + address.lower()

    def to_string(self):
        return self.nickname + " (" + self.name + " " + self.surname + " <" + self.address + ">)"


class UserEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class UserDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        return User(dct['name'], dct['surname'], dct['address'])


def updateFileSystemDb(db_content, db_path, encoder):
    with open(db_path, "w") as outfile:
        json.dump(db_content, outfile, cls=encoder)


# open the user database if not exists create empty folder and file
app_folder_name = ".git-session"
app_db_name = "users.json"
db_file_path = os.path.join(os.environ['HOME'], app_folder_name, app_db_name)

# check if the db file exists
db_exists = os.path.isfile(db_file_path)
if not db_exists:
    # check if the app folder exists if not let's create it
    db_folder_exists = os.path.isdir(
        os.path.join(os.environ['HOME'], app_folder_name))
    if not db_folder_exists:
        os.makedirs(os.path.join(os.environ['HOME'], app_folder_name))

    # create the empty db
    empty_db = []
    updateFileSystemDb(empty_db, db_file_path, UserEncoder)

# load the user db
dbcontext = json.load(open(db_file_path), cls=UserDecoder)

# parse the user commands
parser = argparse.ArgumentParser()

# available commands
parser.add_argument('--list-user', action="store_true",
                    help='List the available users')
parser.add_argument(
    '--add-user', help='Add a new user: Name Surname <email@address>')
parser.add_argument('--rm-user', help='Remove a user: name.surname')

parser.add_argument(
    '--login', help='Login with the desired user: name.surname')
parser.add_argument('--logout', action="store_true",
                    help='Logout from the last login')

# parsing the recognized and the reserved git commands
args, args_to_git = parser.parse_known_args()
# this flag prevents to execute the default git command
# when we are working with the wrapper
wrapper_command_executed = False

if args.list_user:
    wrapper_command_executed = True

    # print out the list of users
    for user in dbcontext:
        print(user.to_string())

if args.add_user:
    wrapper_command_executed = True

    try:
        # before the first space there is only the name
        name_pieces = args.add_user.split(" ")
        # after the first space to the end there is the surname
        # and the email address
        surname_and_address = name_pieces[-1].split("<")

        # assign name
        name = name_pieces[0]

        # get surname
        surname = " ".join(name_pieces[1:-1])
        # if the surname is a composition of multiple words
        # we merge them adding a space
        if(len(surname) > 0):
            surname += " " + surname_and_address[0]
        else:
            surname = surname_and_address[0]

        # get email
        email = surname_and_address[1][0:-1]

        # build the candicate instance
        candidateUser = User(name, surname, email)

        # checking for duplication
        # special case if the db is empty
        if len(dbcontext) <= 0 or len([x for x in dbcontext if x.id == candidateUser.id]) == 0:
            dbcontext.append(candidateUser)
            updateFileSystemDb(dbcontext, db_file_path, UserEncoder)
            print("The candidate user is successfully added")
        else:
            print("The candidate user is already there")
    except:
        print("Unable to add the requested user")

if args.rm_user:
    wrapper_command_executed = True
    nickname_to_be_removed = args.rm_user

    # get the list of matching user by nickname
    matches = [x for x in dbcontext if x.nickname == nickname_to_be_removed]

    # erase the entry and update the db
    if len(matches) > 0:
        dbcontext.remove(matches[0])
        updateFileSystemDb(dbcontext, db_file_path, UserEncoder)
        print("The candidate user is successfully removed")
    else:
        print("The candidate user is not there")

if args.login:
    wrapper_command_executed = True
    nickname_to_be_logged = args.login

    # get the list of matching user by nickname
    matches = [x for x in dbcontext if x.nickname == nickname_to_be_logged]

    # unset the previous git config and set the desired one
    if len(matches) > 0:
        os.system("git config --unset-all user.name")
        os.system("git config --unset-all user.email")

        os.system("git config user.name \"" +
                  matches[0].name + " " + matches[0].surname + "\"")
        os.system("git config user.email " + matches[0].address)
        print(matches[0].nickname + " enabled")
    else:
        print("The candidate user is not there")


if args.logout:
    wrapper_command_executed = True

    # unset the variable
    os.system("git config --unset-all user.name")
    os.system("git config --unset-all user.email")

if not wrapper_command_executed:

    name_is_setup = os.popen("git config --get user.name").read().rstrip("\n")
    email_is_setup = os.popen("git config --get user.email").read().rstrip("\n")

    if len(name_is_setup) <= 0 or len(email_is_setup) <= 0:
        print("Missing username configuration")
    else:
        # Execute the requested git command
        prefix_git_cmd_string = "git"
        cmd_string_list = []

        # convert the list of strings into a single spaced string
        args_to_git_string = " ".join(args_to_git)

        # append to the base git command the arguments
        cmd_string_list.append(prefix_git_cmd_string)
        cmd_string_list.append(args_to_git_string)

        # convert the final string list
        cmd_string = " ".join(cmd_string_list)

        # running the desired command
        # providing information about the running user
        print("Running git with: " + name_is_setup + "<" + email_is_setup + ">")
        os.system(cmd_string)
