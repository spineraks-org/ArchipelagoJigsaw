# Jigsaw Puzzles for Archipelago Setup Guide

The most up-to-date set up steps can be found on the [#jigsaw channel](https://discord.com/channels/731205301247803413/1409148531637489775) in the [Archipelago discord](https://discord.gg/archipelago).
## Required Software
- Browser
- [Archipelago Launcher](https://github.com/ArchipelagoMW/Archipelago/releases/latest)
- [Jigsaw APWorld](https://github.com/spineraks-org/ArchipelagoJigsaw/releases/latest)

## General Concept

1. Download and install the most recent [Archipelago Launcher](https://github.com/ArchipelagoMW/Archipelago/releases/latest)
1. Download the most recent [Jigsaw APWorld](https://github.com/spineraks-org/ArchipelagoJigsaw/releases/latest) and place the `jigsaw.apworld` in the `custom_worlds` folder of your Archipelago install.
1. Generate your player file (details below)
1. Generate & Host your Game (details below)
1. Go to https://jigsaw-ap.netlify.app/ to play your generated game

## Create a Player File

### What is a player file and why do I need one?

Your player file (also known as your "yaml" or "config") contains a set of configuration options which provide the generator 
with information about how it should generate your puzzle. Each unique puzzle (and player of other games) in a multiworld will need its own file.
This setup allows each puzzle and game to be customized, and different puzzles in the same multiworld can all have different options.

### Where do I get a player file? (Easy)

Run the ArchipelagoLauncher.exe from your Archipelago install and click `Options Creator`.
In the new window that opens scroll down on the left until you find `Jigsaw`.
Enter your Player Name in the `Player Name` box. This will be used to log into the server.
Jigsaw has many custom options. Hover over them to get more details.

### Where do I get a player file? (Hard)

Run the ArchipelagoLauncher.exe from your Archipelago install and click `Generate Template Options`.
This will produce a `/Players/Templates` folder in your Archipelago install, which contains default player files for 
every game in your `custom_worlds` and `lib/worlds` folder. You can manually edit the player file using a text editor of your choice.

## Generating a Game

1. After modifying your player file, place it into your Archipelago/player folder (If you are generating for multiworld put a player file in for each player or puzzle you would like in the world)
1. Open the Archipelago Launcher and click "Generate". This will create a zip file in Archipelago/output
1. Navigate to the Archipelago website and go to the Host Game page (top right menu)
1. Click upload file and pass it the .zip created in your output folder
1. Click the "Create New Room" link.
1. Navigate to https://jigsaw-ap.netlify.app/ and use the Host and Port provided to you by the AP website and the PlayerName from your player file.
1. You will have the option to upload a custom image or use a [Default Pictures](https://jigsaw-ap.netlify.app/images.html)
1. Solve the Puzzle

## Joining a MultiWorld Game

When you join a multiworld game, you will be asked to provide your player file to whoever is hosting.
1. Provide your player file to whoever is hosting
1. Navigate to https://jigsaw-ap.netlify.app/ and use the Host and Port provided to you and the PlayerName from your player file.
1. You will have the option to upload a custom image or use a [Default Pictures](https://jigsaw-ap.netlify.app/images.html)
1. Solve the Puzzle