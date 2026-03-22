# AgenticNFT

An ERC-721 NFT standard on X Layer that **can only be minted by OKX Agentic Wallet** (AA smart contract wallets). Regular EOA wallets are permanently excluded — enforced by the EVM itself.

```
msg.sender.code.length > 0  →  AA wallet  →  CAN mint ✓
msg.sender.code.length == 0 →  EOA wallet →  CANNOT mint ✗
```

## Contract

| | |
|---|---|
| **Address** | `0x5f349ea7dD0ab6b4533f6178e8a4674eb42cD01B` |
| **Network** | X Layer Mainnet (Chain ID: 196) |
| **Standard** | `IAgenticNFT` (ERC-721 extension) |
| **Mint price** | Free |
| **Gas** | Free (X Layer) |
| **Supply** | Unlimited, one per agentic wallet |
| **Explorer** | [OKLink ↗](https://www.oklink.com/xlayer/address/0x5f349ea7dD0ab6b4533f6178e8a4674eb42cD01B) |

## Install the mint skill

Customers install the Claude Code skill with one command:

```sh
curl -sSL https://raw.githubusercontent.com/wizard0x0/agentic_only_nft/main/skill-distribution/install.sh | sh
```

Then open Claude Code and say:

> **"mint my AgenticNFT"**

Claude handles the rest — checks your wallet, confirms, mints, shows the tx.

### Prerequisites

1. [Claude Code](https://claude.ai/claude-code)
2. [OKX Agentic Wallet CLI (onchainos)](https://github.com/okx/onchainos-skills)

---

## Mint manually (CLI)

```bash
onchainos wallet contract-call \
  --to 0x5f349ea7dD0ab6b4533f6178e8a4674eb42cD01B \
  --chain 196 \
  --input-data 0x1249c58b
```

---

## How it works

The `IAgenticNFT` standard defines a single on-chain eligibility rule:

```solidity
function canMint(address minter) public view returns (bool) {
    return minter.code.length > 0;
}
```

On X Layer, OKX Agentic Wallets are Account Abstraction (AA) smart contracts — they have bytecode deployed at their address. Standard EOA wallets (MetaMask, hardware wallets) have no code and revert with `NotAgenticWallet`.

## Repository structure

```
contracts/
  IAgenticNFT.sol          # The new NFT standard (interface)
  AgenticNFT.sol           # ERC-721 implementation
  mocks/MockAAWallet.sol   # Test helper
  test/AgenticNFT.t.sol    # 18 Solidity tests
scripts/
  deploy.js                # Deploy to X Layer mainnet
  deployTestnet.js         # Deploy to X Layer testnet
  prepareCreate2Deploy.js  # CREATE2 deployment via agentic wallet
skill-distribution/
  SKILL.md                 # Claude Code skill definition
  install.sh               # One-line installer for customers
website/
  index.html               # Mint website (reads live from chain)
deployments/
  xlayer.json              # Mainnet deployment info
```

## Develop

```bash
npm install
npm test          # Run 18 Solidity tests
npm run compile   # Compile contracts
```

## License

MIT
