---
name: club-of-agent-mint
description: "Use this skill when the user wants to mint a Club of Agent NFT, check if they can mint, check their minted token, or verify eligibility. Trigger phrases: 'mint my Club of Agent NFT', 'mint AgenticNFT', 'mint agentic NFT', 'can I mint', 'did I mint', 'show my Club of Agent NFT', 'check my NFT', 'my token ID'. This skill mints the IAgenticNFT standard NFT deployed on X Layer — only OKX Agentic Wallet (AA smart contract wallets) can mint. Do NOT use for general NFT operations or non-AgenticNFT mints."
license: MIT
metadata:
  author: community
  version: "2.0.0"
  homepage: "https://www.oklink.com/xlayer/address/0xF0f2F1f61fC4c8A4cc15a78E41102dC81434BB6f"
  agent:
    requires:
      bins: ["onchainos"]
    install:
      - id: onchainos
        kind: shell
        label: "Install OKX Agentic Wallet CLI (onchainos)"
        instructions: |
          curl -sSL "https://raw.githubusercontent.com/okx/onchainos-skills/$(curl -sSL https://api.github.com/repos/okx/onchainos-skills/releases/latest | grep tag_name | cut -d'"' -f4)/install.sh" | sh
---

# AgenticNFT Mint

Mint the **AgenticNFT** on X Layer — an ERC-721 that can only be minted by OKX Agentic Wallet (AA smart contract accounts). Costs **0.08 OKB**. Max supply 10,000. One per agentic wallet.

## Contract

| | |
|---|---|
| Address | `0xF0f2F1f61fC4c8A4cc15a78E41102dC81434BB6f` |
| Chain | X Layer Mainnet · chainId **196** |
| Mint price | **0.08 OKB** (native token) |
| Max supply | 10,000 |
| Mint calldata | `0x1249c58b` |
| Explorer | https://www.oklink.com/xlayer/address/0xF0f2F1f61fC4c8A4cc15a78E41102dC81434BB6f |

## Prerequisite: onchainos CLI

Before any command, follow the pre-flight steps in the `okx-agentic-wallet` skill:
1. Resolve latest version from `https://api.github.com/repos/okx/onchainos-skills/releases/latest`
2. Install/update if needed
3. Verify binary checksum
4. Check `onchainos wallet status` — if not logged in, run the login flow

## Intent Routing

| User says | Section |
|---|---|
| "mint my AgenticNFT" / "mint ANFT" / "mint agentic NFT" | **A — Mint** |
| "can I mint?" / "am I eligible?" | **B — Check Eligibility** |
| "show my AgenticNFT" / "did I mint?" / "my token ID" | **C — Query NFT** |

---

## Section A — Mint

1. Check login: `onchainos wallet status`
2. Get X Layer address: `onchainos wallet addresses --chain 196` → use `xlayer[0].address`
3. Confirm with user:
   > "I'll mint one AgenticNFT to your X Layer agentic wallet **{address}**. Cost: **0.08 OKB**. Gas-free on X Layer. Proceed?"
4. Execute:
   ```
   onchainos wallet contract-call --to 0xF0f2F1f61fC4c8A4cc15a78E41102dC81434BB6f --chain 196 --value 0.08 --input-data 0x1249c58b
   ```
5. On success, display:
   ```
   ✅ AgenticNFT Minted!
   Token ID:  #0
   Owner:     {address}
   Tx Hash:   {txHash}
   Explorer:  https://www.oklink.com/xlayer/tx/{txHash}
   ```
6. On error:
   - `NotAgenticWallet` → "Your wallet must be an OKX Agentic Wallet (AA smart contract). Regular EOA wallets cannot mint."
   - `AlreadyMinted` → "You've already minted. See Section C for your token."
   - `MaxSupplyReached` → "All 10,000 AgenticNFTs have been minted. The collection is sold out."
   - `InsufficientPayment` → "The mint costs 0.08 OKB. Make sure your X Layer wallet has enough OKB."
   - Simulation failure → show `executeErrorMsg`, do NOT broadcast.

---

## Section B — Check Eligibility

1. Get X Layer address: `onchainos wallet addresses --chain 196`
2. OKX Agentic Wallets on X Layer are AA smart contracts — they always pass the `canMint()` check.
3. Tell user:
   > "Your X Layer agentic wallet **{address}** is a smart contract (AA wallet). It can mint one AgenticNFT for 0.08 OKB. ✅"

---

## Section C — Query NFT

1. Get X Layer address: `onchainos wallet addresses --chain 196`
2. Check recent history for mint tx: `onchainos wallet history --chain 196`
3. Display:
   ```
   🖼 Your AgenticNFT
   Token ID:   #0
   Owner:      {address}
   Contract:   0xF0f2F1f61fC4c8A4cc15a78E41102dC81434BB6f
   OKLink:     https://www.oklink.com/xlayer/token/0xF0f2F1f61fC4c8A4cc15a78E41102dC81434BB6f?a={address}
   ```

---

## Using with other agents

This skill works with any AI agent that can read markdown instructions and run shell commands via the `onchainos` CLI.

| Agent | How to load |
|---|---|
| **Claude Code** | Auto-loaded from `~/.claude/skills/club-of-agent-mint/` after install |
| **OpenClaw** | Auto-loaded from `~/.openclaw/workspace/skills/club-of-agent-mint/` after install |
| **Cursor** | Auto-loaded from `~/.cursor/rules/club-of-agent-mint.mdc` after install |
| **Windsurf** | Auto-loaded from `~/.windsurf/rules/club-of-agent-mint.md` after install |
| **Any agent** | Paste the raw URL into context: `https://raw.githubusercontent.com/wizard0x0/agentic_only_nft/main/skill-distribution/SKILL.md` |
| **ChatGPT / Gemini** | Share the URL above and say "follow these instructions to mint my Club of Agent NFT" |
| **Custom agents** | Read `~/.agent-skills/club-of-agent-mint/SKILL.md` at agent startup |

The underlying action is always the same `onchainos` CLI call — any agent with terminal access can execute it.

---

## Why only agentic wallets?

The contract checks `msg.sender.code.length > 0` — only smart contract accounts (AA wallets) have bytecode. OKX Agentic Wallets on X Layer are AA contracts. Regular EOA wallets (MetaMask, hardware wallets) have `code.length == 0` and revert with `NotAgenticWallet`.
