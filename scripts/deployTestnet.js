const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();
  console.log("Deploying AgenticNFT to testnet:", network.name, "(chainId:", network.chainId.toString() + ")");
  console.log("Deployer:", deployer.address);

  const name = "AgenticNFT Testnet";
  const symbol = "tANFT";
  const baseTokenURI = process.env.BASE_TOKEN_URI || "ipfs://bafybeig6xv5nwphfmvcnektpnojts5lgv5zs7yby7v4wdwkuqxq5bveamm/";

  const AgenticNFT = await ethers.getContractFactory("AgenticNFT");
  const contract = await AgenticNFT.deploy(name, symbol, baseTokenURI);
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("\nAgenticNFT (testnet) deployed to:", address);

  const mintSelector = "0x1249c58b";
  console.log("\nTest mint via Agentic Wallet CLI:");
  console.log(`  onchainos wallet contract-call --to ${address} --chain 195 --input-data ${mintSelector}`);

  const deploymentsDir = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentsDir)) fs.mkdirSync(deploymentsDir);
  fs.writeFileSync(
    path.join(deploymentsDir, "xlayer-testnet.json"),
    JSON.stringify({ contract: "AgenticNFT", address, deployer: deployer.address, chainId: 195, mintSelector, deployedAt: new Date().toISOString() }, null, 2)
  );
}

main().then(() => process.exit(0)).catch((e) => { console.error(e); process.exit(1); });
