const { expect } = require("chai");
const { ethers } = require("hardhat");

// Helper contract deployed in tests to simulate an AA wallet (smart contract caller)
const MOCK_AA_WALLET_ABI = [
  "function mint(address nftContract) external returns (uint256)",
  "function mintAndCheck(address nftContract) external returns (uint256, address)",
];

describe("AgenticNFT", function () {
  let agenticNFT;
  let owner;
  let eoa1;
  let eoa2;
  let mockAAWallet1;
  let mockAAWallet2;

  const NAME = "AgenticNFT";
  const SYMBOL = "ANFT";
  const BASE_URI = "ipfs://QmTest/";

  beforeEach(async function () {
    [owner, eoa1, eoa2] = await ethers.getSigners();

    // Deploy the AgenticNFT contract
    const AgenticNFT = await ethers.getContractFactory("AgenticNFT");
    agenticNFT = await AgenticNFT.deploy(NAME, SYMBOL, BASE_URI);
    await agenticNFT.waitForDeployment();

    // Deploy mock AA wallet contracts (simulate OKX Agentic Wallet smart contract accounts)
    const MockAAWallet = await ethers.getContractFactory("MockAAWallet");
    mockAAWallet1 = await MockAAWallet.deploy();
    await mockAAWallet1.waitForDeployment();
    mockAAWallet2 = await MockAAWallet.deploy();
    await mockAAWallet2.waitForDeployment();
  });

  // ─────────────────────────── Deployment ──────────────────────────────────

  describe("Deployment", function () {
    it("Should set the correct name and symbol", async function () {
      expect(await agenticNFT.name()).to.equal(NAME);
      expect(await agenticNFT.symbol()).to.equal(SYMBOL);
    });

    it("Should set the correct owner", async function () {
      expect(await agenticNFT.owner()).to.equal(owner.address);
    });

    it("Should start with 0 total supply", async function () {
      expect(await agenticNFT.totalSupply()).to.equal(0);
    });

    it("Should store the base URI", async function () {
      expect(await agenticNFT.baseURI()).to.equal(BASE_URI);
    });
  });

  // ─────────────────────────── canMint ─────────────────────────────────────

  describe("canMint()", function () {
    it("Returns false for EOA addresses (no code)", async function () {
      expect(await agenticNFT.canMint(eoa1.address)).to.equal(false);
      expect(await agenticNFT.canMint(eoa2.address)).to.equal(false);
    });

    it("Returns true for smart contract addresses (AA wallets)", async function () {
      expect(await agenticNFT.canMint(await mockAAWallet1.getAddress())).to.equal(true);
      expect(await agenticNFT.canMint(await mockAAWallet2.getAddress())).to.equal(true);
    });

    it("Returns true for the AgenticNFT contract itself", async function () {
      expect(await agenticNFT.canMint(await agenticNFT.getAddress())).to.equal(true);
    });
  });

  // ─────────────────────────── mint() — AA wallets ─────────────────────────

  describe("mint() — AA wallet callers", function () {
    it("AA wallet can mint successfully", async function () {
      const nftAddress = await agenticNFT.getAddress();
      const tx = await mockAAWallet1.mint(nftAddress);
      const receipt = await tx.wait();

      expect(await agenticNFT.totalSupply()).to.equal(1);
      expect(await agenticNFT.hasMinted(await mockAAWallet1.getAddress())).to.equal(true);
    });

    it("Minted token is owned by the AA wallet", async function () {
      const nftAddress = await agenticNFT.getAddress();
      await mockAAWallet1.mint(nftAddress);

      const aa1Addr = await mockAAWallet1.getAddress();
      const tokenId = await agenticNFT.agentTokenId(aa1Addr);
      expect(await agenticNFT.ownerOf(tokenId)).to.equal(aa1Addr);
    });

    it("Emits AgenticMint event with correct args", async function () {
      const nftAddress = await agenticNFT.getAddress();
      const aa1Addr = await mockAAWallet1.getAddress();

      await expect(mockAAWallet1.mint(nftAddress))
        .to.emit(agenticNFT, "AgenticMint")
        .withArgs(aa1Addr, 0);
    });

    it("Token IDs increment correctly across multiple AA wallets", async function () {
      const nftAddress = await agenticNFT.getAddress();
      await mockAAWallet1.mint(nftAddress);
      await mockAAWallet2.mint(nftAddress);

      expect(await agenticNFT.totalSupply()).to.equal(2);
      expect(await agenticNFT.agentTokenId(await mockAAWallet1.getAddress())).to.equal(0);
      expect(await agenticNFT.agentTokenId(await mockAAWallet2.getAddress())).to.equal(1);
    });

    it("Sets correct token URI after mint", async function () {
      const nftAddress = await agenticNFT.getAddress();
      await mockAAWallet1.mint(nftAddress);

      const tokenId = await agenticNFT.agentTokenId(await mockAAWallet1.getAddress());
      const uri = await agenticNFT.tokenURI(tokenId);
      expect(uri).to.equal(BASE_URI + "0");
    });
  });

  // ─────────────────────────── mint() — EOA blocked ────────────────────────

  describe("mint() — EOA callers (blocked)", function () {
    it("EOA cannot mint — reverts with NotAgenticWallet", async function () {
      await expect(agenticNFT.connect(eoa1).mint())
        .to.be.revertedWithCustomError(agenticNFT, "NotAgenticWallet")
        .withArgs(eoa1.address);
    });

    it("EOA2 also cannot mint", async function () {
      await expect(agenticNFT.connect(eoa2).mint())
        .to.be.revertedWithCustomError(agenticNFT, "NotAgenticWallet")
        .withArgs(eoa2.address);
    });

    it("Total supply stays 0 after failed EOA mint attempts", async function () {
      await agenticNFT.connect(eoa1).mint().catch(() => {});
      await agenticNFT.connect(eoa2).mint().catch(() => {});
      expect(await agenticNFT.totalSupply()).to.equal(0);
    });
  });

  // ─────────────────────────── One-per-wallet ──────────────────────────────

  describe("One NFT per AA wallet", function () {
    it("AA wallet cannot mint twice — reverts with AlreadyMinted", async function () {
      const nftAddress = await agenticNFT.getAddress();
      await mockAAWallet1.mint(nftAddress);

      await expect(mockAAWallet1.mint(nftAddress))
        .to.be.revertedWithCustomError(agenticNFT, "AlreadyMinted")
        .withArgs(await mockAAWallet1.getAddress());
    });

    it("hasMinted tracks state correctly", async function () {
      const nftAddress = await agenticNFT.getAddress();
      const aa1Addr = await mockAAWallet1.getAddress();
      const aa2Addr = await mockAAWallet2.getAddress();

      expect(await agenticNFT.hasMinted(aa1Addr)).to.equal(false);
      await mockAAWallet1.mint(nftAddress);
      expect(await agenticNFT.hasMinted(aa1Addr)).to.equal(true);
      expect(await agenticNFT.hasMinted(aa2Addr)).to.equal(false);
    });
  });

  // ─────────────────────────── Owner functions ─────────────────────────────

  describe("Owner functions", function () {
    it("Owner can update base URI", async function () {
      const newURI = "https://api.agenticnft.xyz/metadata/";
      await agenticNFT.connect(owner).setBaseURI(newURI);
      expect(await agenticNFT.baseURI()).to.equal(newURI);
    });

    it("Non-owner cannot update base URI", async function () {
      await expect(
        agenticNFT.connect(eoa1).setBaseURI("https://evil.com/")
      ).to.be.revertedWithCustomError(agenticNFT, "OwnableUnauthorizedAccount");
    });
  });

  // ─────────────────────────── ERC-721 compliance ──────────────────────────

  describe("ERC-721 compliance", function () {
    it("Supports ERC-721 interface", async function () {
      expect(await agenticNFT.supportsInterface("0x80ac58cd")).to.equal(true); // ERC721
    });

    it("Supports ERC-721Metadata interface", async function () {
      expect(await agenticNFT.supportsInterface("0x5b5e139f")).to.equal(true); // ERC721Metadata
    });

    it("AA wallet can transfer minted NFT to EOA", async function () {
      const nftAddress = await agenticNFT.getAddress();
      await mockAAWallet1.mint(nftAddress);

      const aa1Addr = await mockAAWallet1.getAddress();
      const tokenId = await agenticNFT.agentTokenId(aa1Addr);

      // Transfer via mock wallet to EOA
      await mockAAWallet1.transferNFT(nftAddress, eoa1.address, tokenId);
      expect(await agenticNFT.ownerOf(tokenId)).to.equal(eoa1.address);
    });
  });
});
