// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title IAgenticNFT — The Agentic NFT Standard
/// @notice An NFT standard that can only be minted by AI Agent wallets (AA smart contract wallets).
///         This ensures each NFT is bound to a verifiably autonomous, on-chain agent identity.
///
/// @dev The standard enforces that `msg.sender` must be a smart contract (code.length > 0),
///      which on X Layer corresponds to OKX Agentic Wallet (AA wallet) addresses.
///      Regular EOAs (externally owned accounts) are excluded from minting.
///
/// @custom:eip Extends ERC-721. Recommended deployment chain: X Layer (chainId 196).
interface IAgenticNFT {
    /// @notice Emitted when an agentic wallet mints an NFT
    /// @param minter The AA wallet address that minted
    /// @param tokenId The minted token ID
    event AgenticMint(address indexed minter, uint256 indexed tokenId);

    /// @notice Returns true if the given address is eligible to mint (must be a smart contract)
    /// @param minter The address to check
    /// @return True if `minter` has deployed bytecode (is a smart contract / AA wallet)
    function canMint(address minter) external view returns (bool);

    /// @notice Mint one AgenticNFT to the calling AA wallet
    /// @dev Reverts if `msg.sender` is not a smart contract, or has already minted.
    ///      Free to call — no ETH payment required.
    /// @return tokenId The newly minted token ID
    function mint() external returns (uint256 tokenId);
}
