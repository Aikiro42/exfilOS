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

This game is a/an:
- **Text-adventure:** This game is like the text adventures of old, which you play by passing `<command> <object>` commands like `move north`, `open chest`, `attack zombie`. The difference is that this game more intuitively matches text-based adventure interaction mechanics by making it more literal.
- **Extraction game:** You go into a (randomly-generated) "map" i.e. Host, you loot "treasure" i.e. Files, you kill enemies i.e. threats, you find a place to "extract" i.e. direct link back to `Home` host, before the timer runs out i.e. the Government noticing a lurker.
- **Puzzle game:** This game is educational in a sense that it aims to gameify various Computer Science subjects like cryptography, DSA.

### Commands

All commands are implemented on the shell.

Commonly known terminal commands: `ls`, `cd`, `cp`, `mv`, `mkdir`

Custom commands:
- `cache`: accesses your cache filesystem.
- `download`: "pick up" files. Equivalent to `wget`, `curl`
- `upload`: "drop" files
- `send`: "sell" files (only works at `Home`)
- `open`: "interact" with files.
- `run`: "attack" with the specified program: see combat


### Stats
- Integrity: Your "health" stat.
  - The lower your health stat, the higher the chance your commands will fail.
- RAM: Your cache size.
- Storage: Your Home storage size.
- CPU speed: How fast your commands run.
- Encryption: Your "stealth" stat. The higher it is, the longer your timer, and the less likely Threats will initiate combat with you. Must be capped to a point where
  - the initiative to engage threats is 100% on you.
  - the timer is 15 minutes.
- Daemons: Available "attacks" with cooldowns. One of them is always available but deals the least amount of damage.
- IPC (Instructions per Cycle): Affects "attack power"
- Core Count: Affects how many hits an attack can do.

### Equipment

- Case
- Motherboard
- CPU
- CPU Cooler
- RAM
- Storage (HDD / SSD / NVMe)
- GPU
- Power Supply (PSU)
- Network Adapter (Ethernet / Wi-Fi)
- Sound Card
- Fans
- Thermal Paste
- Optional-but-common (still PC-builder intuitive):
- Optical Drive
- Expansion Card (PCIe)
- USB Controller Card
- Capture Card

### Combat

- Directories have a chance to contain a threat.
- Whenever you enter or exit a directory with a threat, there is a chance that the threat initiates a "fight" with you.

**Combat loop:**
1. The threat throws you a puzzle.
2. You solve the puzzle: submit the wrong answer, and your `Integrity` stat takes a hit.
3. You have an opportunity to "attack" the threat with an installed program.
4. The threat takes a hit.

**Attacks**
- "Attacks" i.e. Defensive Programs are run via `run <program>`.
- Each program has two effects when run: in-combat and out-of-combat.

### Puzzles
Common puzzles
These are basic puzzles that can be done by hand.
- Type a line of code
  - The code contains zero-width characters, so that it is 
- Sort a list

Uncommon puzzles
- Flatten a list.

Rare puzzles:
These are common leetcode puzzles.
- Decrypt text
- Decompress data
- Largest substring
- Inverse binary tree
- Array implementation of a binary tree

### Loot

`File`s are hashed on generation. If a `File`'s hash matches its hash, then it is authentic. Ergo, files made by the player must always be empty; that way, it is more difficult to make monetary exploits.

The following code is used to generate a file's hash from its data string:
```python
# Simple rolling hash, FNV-style; see https://en.wikipedia.org/wiki/Rolling_hash
def hash(s: str) -> int:
    h = 2166136261  # FNV offset basis
    for c in s:
        h = (h ^ ord(c)) * 16777619
        h &= 0xFFFFFFFF  # force 32-bit wrap
    h ^= len(s)
    return h
```


### Code

- `User` is the player class. It holds basic game values, and has a "cache" `FileSystem`, which acts as the "backpack".
  - `User` also has a list of "attacks" i.e. programs that have cooldowns.
- `Mollusk` is the shell class.
  - It keeps track of the current working directory.
- `Host` is the "stage" class.
- `FileSystem` is the "movement" class. It is responsible for parsing and resolving paths.