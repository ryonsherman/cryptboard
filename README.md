# cryptboard

**Public encrypted dead drops over GitHub.**

Post encrypted messages to a public GitHub repo. Anyone can see the message
files exist, but without the right ID they're just random noise. Since every
message is tried by brute force during receive, there's no way to tell which
message belongs to which recipient — or even if any given message is real at
all.

> Plausible deniability is a feature, not a bug.

## How it works

- **Send**: Encrypt a message with the recipient's ID (a hex key). Push the
  ciphertext as a tiny JSON file to `messages/` via a pull request. A GitHub
  Actions workflow auto-validates and merges it.
- **Receive**: Shallow-clone the repo's `messages/` directory. Try every file
  — each header decrypts in microseconds. Skip what doesn't match, decrypt
  what does. Only you know which blobs are yours.

No accounts, no metadata, no central server (beyond GitHub itself).

## Dependencies

- Python 3.8+
- `cryptography` (`pip install cryptography`)
- `git`
- `gh` (GitHub CLI) — authenticated — for sending

## Install

Just download the script:

```
curl -LO https://raw.githubusercontent.com/ryonsherman/cryptboard/main/cryptboard
chmod +x cryptboard
```

Optionally put it somewhere on your `$PATH`.

## Usage

### Generate an ID

```
cryptboard gen-id
```

Prints a 64-character hex string. This is the **shared secret** — send it to
your recipient out of band (Signal, in person, etc.). The ID is your identity;
anyone who has it can read messages encrypted for it.

### Send a message

```
cryptboard send <id> "<message>"
```

Encrypts the message so only the holder of `<id>` can read it, opens a pull
request on GitHub, and prints confirmation when the PR lands.

### Receive messages

```
cryptboard receive <id> [--since 2025-01-01]
```

Downloads only the message files added after `--since` (defaults to 1 month
ago) and tries each one. Prints every message that decrypts successfully.
If your ID has received multiple messages, you'll see them all.

## Example

Generate an ID (your shared secret):

```
$ cryptboard gen-id
a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
```

Send a message:

```
$ cryptboard send a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2 "Hello from e2e test!"
Message queued and will post automatically
```

The script forks the repo, commits the encrypted message, and opens a PR. The
workflow validates it's a new file under `messages/`, confirms the format, and
auto-merges — all in a few seconds.

Receive messages (same ID):

```
$ cryptboard receive a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
Hello from e2e test!
```

Multiple messages sent to the same ID appear on separate lines. A wrong ID
returns nothing:

```
$ cryptboard receive deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef
No messages found
```

The `--since` flag narrows the window:

```
$ cryptboard receive a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2 --since 2026-06-07
Hello from e2e test!
```

## The repo format

Each message is a file in `messages/` named `<uuid>.json`:

```json
{"h":"<base64 AES-CBC header>","b":"<base64 AES-CBC body>"}
```

- **h**: Encrypted form of the fixed plaintext `CRYPTBOARD`. Used as a
  fast-match header so receiving is O(n) header decrypts + O(1) body decrypts.
- **b**: The encrypted message body.
- **Key**: SHA-256 of the ID hex string → 32-byte AES-256 key.
- No sender info, no timestamps, no metadata of any kind.

## Security & privacy

- Encryption is **AES-256-CBC** with a random IV per message.
- The ID is the key. Lose it, lose your messages.
- The repo is **append-only**: the CI workflow rejects any PR that modifies
  or deletes existing files.
- Even with the repo cloned locally, an attacker cannot determine which
  messages belong to you without your ID.
- There is no way to prove a given message is intended for a given recipient,
  or that it contains a real message at all.

## Limitations

- The `send` command requires `gh` to be authenticated with a GitHub account.
- The `receive` command does a lightweight shallow clone of the last ~30 days
  by default. Use `--since` to adjust the window.
- Rate limits on unauthenticated GitHub API usage may affect heavy use.
