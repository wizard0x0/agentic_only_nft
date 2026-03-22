// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./IAgenticNFT.sol";

/// @title AgenticNFT
/// @notice ERC-721 NFT implementation of the IAgenticNFT standard.
///         Mint is restricted to OKX Agentic Wallet (AA smart contract wallets).
///         Costs 0.08 OKB. One NFT per agentic wallet. Max supply 10,000.
///
/// @dev Deployed on X Layer (chainId 196) where OKX Agentic Wallets are AA contracts.
///      The minting check uses `msg.sender.code.length > 0`:
///        - AA wallets (smart contracts): code.length > 0  → CAN mint ✓
///        - EOA accounts:                 code.length == 0 → CANNOT mint ✗
contract AgenticNFT is ERC721, Ownable, IAgenticNFT {
    // ─────────────────────────── Errors ───────────────────────────────────────

    error NotAgenticWallet(address caller);
    error AlreadyMinted(address caller);
    error MaxSupplyReached();
    error InsufficientPayment(uint256 sent, uint256 required);

    // ─────────────────────────── Constants ────────────────────────────────────

    /// @notice Mint price in OKB (native token)
    uint256 public constant MINT_PRICE = 0.08 ether;

    /// @notice Maximum number of NFTs that can ever be minted
    uint256 public constant MAX_SUPPLY = 10_000;

    // ─────────────────────────── State ────────────────────────────────────────

    /// @notice Total number of NFTs minted
    uint256 public totalSupply;

    /// @notice Address that receives mint proceeds
    address public treasury;

    /// @notice Whether a given address has already minted
    mapping(address => bool) public hasMinted;

    /// @notice The tokenId owned by a given agentic wallet (valid only if hasMinted[addr])
    mapping(address => uint256) public agentTokenId;

    /// @notice Base URI for token metadata
    string private _baseTokenURI;

    // ─────────────────────────── Constructor ──────────────────────────────────

    /// @param name_        Token name (e.g. "AgenticNFT")
    /// @param symbol_      Token symbol (e.g. "ANFT")
    /// @param baseTokenURI Base URI for metadata (IPFS/Arweave/HTTP)
    /// @param treasury_    Address to receive mint proceeds
    constructor(
        string memory name_,
        string memory symbol_,
        string memory baseTokenURI,
        address treasury_
    ) ERC721(name_, symbol_) Ownable(msg.sender) {
        require(treasury_ != address(0), "Zero treasury");
        _baseTokenURI = baseTokenURI;
        treasury = treasury_;
    }

    // ─────────────────────────── IAgenticNFT ──────────────────────────────────

    /// @inheritdoc IAgenticNFT
    function canMint(address minter) public view override returns (bool) {
        return minter.code.length > 0;
    }

    /// @inheritdoc IAgenticNFT
    function mint() external payable override returns (uint256 tokenId) {
        if (!canMint(msg.sender)) revert NotAgenticWallet(msg.sender);
        if (hasMinted[msg.sender]) revert AlreadyMinted(msg.sender);
        if (totalSupply >= MAX_SUPPLY) revert MaxSupplyReached();
        if (msg.value < MINT_PRICE) revert InsufficientPayment(msg.value, MINT_PRICE);

        tokenId = totalSupply;
        totalSupply += 1;

        hasMinted[msg.sender] = true;
        agentTokenId[msg.sender] = tokenId;

        _safeMint(msg.sender, tokenId);
        emit AgenticMint(msg.sender, tokenId);

        // Forward payment to treasury
        (bool ok, ) = treasury.call{value: msg.value}("");
        require(ok, "Transfer failed");
    }

    // ─────────────────────────── Owner admin ──────────────────────────────────

    /// @notice Update the base URI (owner only)
    function setBaseURI(string calldata newBaseURI) external onlyOwner {
        _baseTokenURI = newBaseURI;
    }

    /// @notice Update the treasury address (owner only)
    function setTreasury(address newTreasury) external onlyOwner {
        require(newTreasury != address(0), "Zero treasury");
        treasury = newTreasury;
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

    function _toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) return "0";
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) { digits++; temp /= 10; }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
}
