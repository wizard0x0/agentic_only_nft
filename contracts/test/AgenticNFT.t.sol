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

    address internal treasury = address(0xE85CD5681567c6a5D141b9fD1d2eC58C5736fF55);
    string internal constant BASE_URI = "ipfs://QmTest/";
    uint256 internal constant PRICE = 0.08 ether;

    // ─────────────────────────── Setup ────────────────────────────────────────

    function setUp() external {
        nft = new AgenticNFT("AgenticNFT", "ANFT", BASE_URI, treasury);
        aaWallet1 = new MockAAWallet();
        aaWallet2 = new MockAAWallet();
        // Fund mocks so they can pay mint price
        payable(address(aaWallet1)).transfer(1 ether);
        payable(address(aaWallet2)).transfer(1 ether);
    }

    // ─────────────────────────── Deployment ──────────────────────────────────

    function test_name() external view {
        require(keccak256(bytes(nft.name())) == keccak256(bytes("AgenticNFT")), "wrong name");
    }

    function test_symbol() external view {
        require(keccak256(bytes(nft.symbol())) == keccak256(bytes("ANFT")), "wrong symbol");
    }

    function test_initialSupplyIsZero() external view {
        require(nft.totalSupply() == 0, "supply should be 0");
    }

    function test_baseURI() external view {
        require(keccak256(bytes(nft.baseURI())) == keccak256(bytes(BASE_URI)), "wrong base URI");
    }

    function test_mintPrice() external view {
        require(nft.MINT_PRICE() == PRICE, "wrong mint price");
    }

    function test_maxSupply() external view {
        require(nft.MAX_SUPPLY() == 10_000, "wrong max supply");
    }

    function test_treasury() external view {
        require(nft.treasury() == treasury, "wrong treasury");
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
        aaWallet1.mint(address(nft), PRICE);
        require(nft.totalSupply() == 1, "supply should be 1");
        require(nft.hasMinted(address(aaWallet1)), "hasMinted should be true");
    }

    function test_mintedTokenOwnedByAAWallet() external {
        aaWallet1.mint(address(nft), PRICE);
        uint256 tokenId = nft.agentTokenId(address(aaWallet1));
        require(nft.ownerOf(tokenId) == address(aaWallet1), "owner should be AA wallet");
    }

    function test_tokenIds_incrementAcrossMultipleAAWallets() external {
        aaWallet1.mint(address(nft), PRICE);
        aaWallet2.mint(address(nft), PRICE);
        require(nft.totalSupply() == 2, "supply should be 2");
        require(nft.agentTokenId(address(aaWallet1)) == 0, "first token ID should be 0");
        require(nft.agentTokenId(address(aaWallet2)) == 1, "second token ID should be 1");
    }

    function test_tokenURI_setCorrectlyAfterMint() external {
        aaWallet1.mint(address(nft), PRICE);
        uint256 tokenId = nft.agentTokenId(address(aaWallet1));
        string memory uri = nft.tokenURI(tokenId);
        require(
            keccak256(bytes(uri)) == keccak256(bytes(string(abi.encodePacked(BASE_URI, "0")))),
            "wrong token URI"
        );
    }

    function test_mint_transfersOKBToTreasury() external {
        uint256 before = treasury.balance;
        aaWallet1.mint(address(nft), PRICE);
        require(treasury.balance == before + PRICE, "treasury should receive PRICE");
    }

    // ─────────────────────────── mint — payment checks ───────────────────────

    function test_mint_revertsOnInsufficientPayment() external {
        try aaWallet1.mint(address(nft), PRICE - 1) {
            revert("should have reverted with InsufficientPayment");
        } catch {
            // expected
        }
    }

    function test_mint_revertsOnZeroPayment() external {
        try aaWallet1.mint(address(nft), 0) {
            revert("should have reverted with InsufficientPayment");
        } catch {
            // expected
        }
    }

    // ─────────────────────────── One-per-wallet ──────────────────────────────

    function test_AAWallet_cannotMintTwice_revertsAlreadyMinted() external {
        aaWallet1.mint(address(nft), PRICE);
        try aaWallet1.mint(address(nft), PRICE) {
            revert("should have reverted with AlreadyMinted");
        } catch {
            // expected
        }
        require(nft.totalSupply() == 1, "supply should still be 1");
    }

    function test_hasMinted_tracksStateCorrectly() external {
        require(!nft.hasMinted(address(aaWallet1)), "should not have minted yet");
        aaWallet1.mint(address(nft), PRICE);
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
        aaWallet1.mint(address(nft), PRICE);
        uint256 tokenId = nft.agentTokenId(address(aaWallet1));
        address recipient = address(0xABCD);
        aaWallet1.transferNFT(address(nft), recipient, tokenId);
        require(nft.ownerOf(tokenId) == recipient, "owner should be recipient after transfer");
    }

    // ─────────────────────────── Owner functions ─────────────────────────────

    function test_owner_canUpdateBaseURI() external {
        string memory newURI = "https://api.agenticnft.xyz/metadata/";
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
