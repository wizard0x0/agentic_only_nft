// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";

/// @dev Test helper: simulates an OKX Agentic Wallet (AA smart contract account).
///      Implements IERC721Receiver so it can safely receive ERC-721 tokens via _safeMint.
///      Used only in tests — never deploy to mainnet.
contract MockAAWallet is IERC721Receiver {
    /// @notice Required by IERC721Receiver — accepts all ERC-721 tokens
    function onERC721Received(
        address, // operator
        address, // from
        uint256, // tokenId
        bytes calldata // data
    ) external pure override returns (bytes4) {
        return IERC721Receiver.onERC721Received.selector;
    }

    /// @notice Call mint() on an IAgenticNFT contract and return the tokenId
    function mint(address nftContract) external returns (uint256 tokenId) {
        (bool ok, bytes memory data) = nftContract.call(
            abi.encodeWithSignature("mint()")
        );
        require(ok, "mint call failed");
        tokenId = abi.decode(data, (uint256));
    }

    /// @notice Transfer an NFT owned by this mock wallet to another address
    function transferNFT(address nftContract, address to, uint256 tokenId) external {
        IERC721(nftContract).transferFrom(address(this), to, tokenId);
    }

    /// @notice Attempt to call setBaseURI (should revert if not owner)
    function callSetBaseURI(address nftContract, string calldata newURI) external {
        (bool ok,) = nftContract.call(
            abi.encodeWithSignature("setBaseURI(string)", newURI)
        );
        require(ok, "setBaseURI succeeded unexpectedly");
    }
}
