# `exfilOS`

A text-based extraction adventure game, where you are tapping into a PC Unit in an alternate universe.

Your goal is to gather as much data and information about the universe while avoiding viruses and government surveillance.

## Setting & Lore

## Gameplay

Your home filesystem is your storage.

You `connect` to a random host, then find a direct connection back to your own Host in the universe before the Government notices you. Along the way, you `cache` files.

It is possible to encounter threats while traversing filesystems. When you encounter threats, you defend against them by running programs or solving their puzzles, whether it be leetcode, cryptographic, or rarely, lore questionnaires.

The more you put in your cache, the slower your commands run.

If the Government notices you lurking, your game is forcibly terminated. If you are compromised by any threat, your game is terminated.

The files you cached from other Hosts are "authentic" and can be `portal`ed back to your universe in exchange for currency. The currency you gain is based on the filesize of the authentic file you portaled home. Editing files removes their authenticity.

When you exit the game properly, your progress is saved. Otherwise, your progress is reset.

## Developer Notes

### Design



### Code

- `User` is the player class. It holds basic game values, and has a "cache" `FileSystem`, which acts as the "backpack".
  - `User` also has a list of "attacks" i.e. programs that have cooldowns.
- `Mollusk` is the shell class.
  - It keeps track of the current working directory.
- `Host` is the "stage" class.
- `FileSystem` is the "movement" class. It is responsible for parsing and resolving paths.