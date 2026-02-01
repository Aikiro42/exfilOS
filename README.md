# `exfilOS`

A text-based extraction adventure game, where you are tapping into a PC Unit in an alternate universe.

Your goal is to gather as much data and information about the universe while avoiding viruses and government surveillance.

## Setting & Lore



## Gameplay

Your home filesystem is your storage.

You `connect` to a random host, then find a direct connection back to your own Host in the universe. Along the way, you `cache` files. When you encounter viruses, you defend against them by running programs.

The files you cached from other Hosts are "authentic" and can be `portal`ed back to your universe in exchange for currency. The currency you gain is based on the filesize of the authentic file you portaled home. Editing files removes their authenticity.

## Developer Notes

- `User` is the player class. It holds basic game values, and has a "cache" `FileSystem`, which acts as the "backpack".
- `Mollusk` is the shell class.
  - It keeps track of the current working directory.
- `Host` is the "stage" class.
- `FileSystem` is the "movement" class. It is responsible for parsing and resolving paths.