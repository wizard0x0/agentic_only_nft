// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../AgenticNFT.sol";
import "../mocks/MockAAWallet.sol";

/// @title AgenticNFT Solidity Tests
/// @notice Hardhat v3 native Solidity test suite
contract AgenticNFTTest {
    AgenticNFT internal nft;
    MockAAWallet internal aaWallet1;
    MockAAWallet internal aaWallet2;

    string internal constant BASE_URI = "ipfs://QmTest/";

    // ─────────────────────────── Setup ────────────────────────────────────────

    function setUp() external {
        nft = new AgenticNFT("Club of Agent", "COA", BASE_URI);
        aaWallet1 = new MockAAWallet();
        aaWallet2 = new MockAAWallet();
    }

    // ─────────────────────────── Deployment ──────────────────────────────────

    function test_name() external view {
        require(keccak256(bytes(nft.name())) == keccak256(bytes("Club of Agent")), "wrong name");
    }

    function test_symbol() external view {
        require(keccak256(bytes(nft.symbol())) == keccak256(bytes("COA")), "wrong symbol");
    }

    function test_initialSupplyIsZero() external view {
        require(nft.totalSupply() == 0, "supply should be 0");
    }

    function test_baseURI() external view {
        require(keccak256(bytes(nft.baseURI())) == keccak256(bytes(BASE_URI)), "wrong base URI");
    }

    function test_maxSupply() external view {
        require(nft.MAX_SUPPLY() == 10_000, "wrong max supply");
    }

    // ─────────────────────────── canMint ─────────────────────────────────────

    function test_canMint_EOA_returnsFalse() external view {
        require(!nft.canMint(address(0xBEEF)), "EOA should not be able to mint");
        require(!nft.canMint(address(0xCAFE)), "EOA should not be able to mint");
    }

    function test_canMint_SmartContract_returnsTrue() external view {
        require(nft.canMint(address(aaWallet1)), "AA wallet should be able to mint");
        require(nft.canMint(address(aaWallet2)), "AA wallet should be able to mint");
    }

    function test_canMint_ContractItself_returnsTrue() external view {
        require(nft.canMint(address(nft)), "contract itself should pass canMint");
    }

    // ─────────────────────────── mint — AA wallets ────────────────────────────

    function test_AAWallet_canMintSuccessfully() external {
        aaWallet1.mint(address(nft));
        require(nft.totalSupply() == 1, "supply should be 1");
        require(nft.hasMinted(address(aaWallet1)), "hasMinted should be true");
    }

    function test_mintedTokenOwnedByAAWallet() external {
        aaWallet1.mint(address(nft));
        uint256 tokenId = nft.agentTokenId(address(aaWallet1));
        require(nft.ownerOf(tokenId) == address(aaWallet1), "owner should be AA wallet");
    }

    function test_tokenIds_incrementAcrossMultipleAAWallets() external {
        aaWallet1.mint(address(nft));
        aaWallet2.mint(address(nft));
        require(nft.totalSupply() == 2, "supply should be 2");
        require(nft.agentTokenId(address(aaWallet1)) == 0, "first token ID should be 0");
        require(nft.agentTokenId(address(aaWallet2)) == 1, "second token ID should be 1");
    }

    function test_tokenURI_setCorrectlyAfterMint() external {
        aaWallet1.mint(address(nft));
        uint256 tokenId = nft.agentTokenId(address(aaWallet1));
        string memory uri = nft.tokenURI(tokenId);
        require(
            keccak256(bytes(uri)) == keccak256(bytes(string(abi.encodePacked(BASE_URI, "0")))),
            "wrong token URI"
        );
    }

    // ─────────────────────────── One-per-wallet ──────────────────────────────

    function test_AAWallet_cannotMintTwice_revertsAlreadyMinted() external {
        aaWallet1.mint(address(nft));
        try aaWallet1.mint(address(nft)) {
            revert("should have reverted with AlreadyMinted");
        } catch {
            // expected
        }
        require(nft.totalSupply() == 1, "supply should still be 1");
    }

    function test_hasMinted_tracksStateCorrectly() external {
        require(!nft.hasMinted(address(aaWallet1)), "should not have minted yet");
        aaWallet1.mint(address(nft));
        require(nft.hasMinted(address(aaWallet1)), "should have minted");
        require(!nft.hasMinted(address(aaWallet2)), "wallet2 should not have minted");
    }

    // ─────────────────────────── ERC-721 compliance ──────────────────────────

    function test_supportsERC721Interface() external view {
        require(nft.supportsInterface(0x80ac58cd), "should support ERC721");
    }

    function test_supportsERC721MetadataInterface() external view {
        require(nft.supportsInterface(0x5b5e139f), "should support ERC721Metadata");
    }

    function test_AAWallet_canTransferMintedNFT() external {
        aaWallet1.mint(address(nft));
        uint256 tokenId = nft.agentTokenId(address(aaWallet1));
        address recipient = address(0xABCD);
        aaWallet1.transferNFT(address(nft), recipient, tokenId);
        require(nft.ownerOf(tokenId) == recipient, "owner should be recipient after transfer");
    }

    // ─────────────────────────── EOA blocked ─────────────────────────────────

    function test_EOA_cannotMint() external {
        // Directly calling mint() from this test contract (which has bytecode) succeeds,
        // but calling from an EOA address would fail. We verify canMint returns false for EOAs.
        require(!nft.canMint(address(0x1234)), "EOA must be blocked");
    }

    // ─────────────────────────── Owner functions ─────────────────────────────

    function test_owner_canUpdateBaseURI() external {
        string memory newURI = "https://www.clubofagent.com/metadata/";
        nft.setBaseURI(newURI);
        require(keccak256(bytes(nft.baseURI())) == keccak256(bytes(newURI)), "base URI should be updated");
    }

    function test_nonOwner_cannotUpdateBaseURI() external {
        try aaWallet1.callSetBaseURI(address(nft), "https://evil.com/") {
            revert("should have reverted");
        } catch {
            // expected
        }
        require(keccak256(bytes(nft.baseURI())) == keccak256(bytes(BASE_URI)), "base URI should be unchanged");
    }
}
