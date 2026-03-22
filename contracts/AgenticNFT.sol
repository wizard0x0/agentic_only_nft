// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./IAgenticNFT.sol";

/// @title AgenticNFT
/// @notice ERC-721 NFT implementation of the IAgenticNFT standard.
///         Mint is restricted to OKX Agentic Wallet (AA smart contract wallets).
///         Free to mint. One NFT per agentic wallet address.
///
/// @dev Deployed on X Layer (chainId 196) where OKX Agentic Wallets are AA contracts.
///      The minting check uses `msg.sender.code.length > 0`:
///        - AA wallets (smart contracts): code.length > 0  → CAN mint ✓
///        - EOA accounts:                 code.length == 0 → CANNOT mint ✗
///
/// @custom:security-contact security@okx.com
contract AgenticNFT is ERC721, Ownable, IAgenticNFT {
    // ─────────────────────────── Errors ───────────────────────────────────────

    /// @dev Reverts when the caller is not an AA smart contract wallet
    error NotAgenticWallet(address caller);

    /// @dev Reverts when the AA wallet has already minted its one token
    error AlreadyMinted(address caller);

    // ─────────────────────────── State ────────────────────────────────────────

    /// @notice Total number of NFTs minted
    uint256 public totalSupply;

    /// @notice Whether a given address has already minted
    mapping(address => bool) public hasMinted;

    /// @notice The tokenId owned by a given agentic wallet (0 if none)
    mapping(address => uint256) public agentTokenId;

    /// @notice Base URI for token metadata
    string private _baseTokenURI;

    // ─────────────────────────── Constructor ──────────────────────────────────

    /// @param name_        Token name (e.g. "AgenticNFT")
    /// @param symbol_      Token symbol (e.g. "ANFT")
    /// @param baseTokenURI Base URI for metadata (IPFS/Arweave/HTTP)
    constructor(
        string memory name_,
        string memory symbol_,
        string memory baseTokenURI
    ) ERC721(name_, symbol_) Ownable(msg.sender) {
        _baseTokenURI = baseTokenURI;
    }

    // ─────────────────────────── IAgenticNFT ──────────────────────────────────

    /// @inheritdoc IAgenticNFT
    /// @notice Returns true if `minter` is a smart contract (code.length > 0).
    ///         On X Layer, OKX Agentic Wallets are AA contracts — they pass this check.
    ///         Regular EOAs (code.length == 0) fail this check.
    function canMint(address minter) public view override returns (bool) {
        return minter.code.length > 0;
    }

    /// @inheritdoc IAgenticNFT
    /// @notice Mint one AgenticNFT to `msg.sender` (must be an OKX Agentic Wallet).
    ///         Free. One mint per agentic wallet address.
    function mint() external override returns (uint256 tokenId) {
        if (!canMint(msg.sender)) {
            revert NotAgenticWallet(msg.sender);
        }
        if (hasMinted[msg.sender]) {
            revert AlreadyMinted(msg.sender);
        }

        tokenId = totalSupply;
        totalSupply += 1;

        hasMinted[msg.sender] = true;
        agentTokenId[msg.sender] = tokenId;

        _safeMint(msg.sender, tokenId);

        emit AgenticMint(msg.sender, tokenId);
    }

    // ─────────────────────────── Owner admin ──────────────────────────────────

    /// @notice Update the base URI (owner only)
    function setBaseURI(string calldata newBaseURI) external onlyOwner {
        _baseTokenURI = newBaseURI;
    }

    // ─────────────────────────── View helpers ─────────────────────────────────

    /// @notice Returns the base URI used for all token metadata
    function baseURI() external view returns (string memory) {
        return _baseTokenURI;
    }

    /// @notice Returns `baseURI + tokenId` for each token
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        _requireOwned(tokenId);
        return string(abi.encodePacked(_baseTokenURI, _toString(tokenId)));
    }

    // ─────────────────────────── Internal ─────────────────────────────────────

    function _baseURI() internal view override returns (string memory) {
        return _baseTokenURI;
    }

    /// @dev Converts uint256 to its decimal string representation
    function _toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) return "0";
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
}
