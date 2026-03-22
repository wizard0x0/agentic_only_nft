const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying AgenticNFT with account:", deployer.address);
  console.log("Balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "OKB");

  const name = "AgenticNFT";
  const symbol = "ANFT";
  // Update this to your actual IPFS/Arweave metadata URI before mainnet deployment
  const baseTokenURI = process.env.BASE_TOKEN_URI || "ipfs://bafybeig6xv5nwphfmvcnektpnojts5lgv5zs7yby7v4wdwkuqxq5bveamm/";

  console.log("\nDeploying AgenticNFT...");
  console.log("  Name:", name);
  console.log("  Symbol:", symbol);
  console.log("  Base URI:", baseTokenURI);

  const AgenticNFT = await ethers.getContractFactory("AgenticNFT");
  const contract = await AgenticNFT.deploy(name, symbol, baseTokenURI);
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("\nAgenticNFT deployed to:", address);
  console.log("Network:", (await ethers.provider.getNetwork()).name);
  console.log("Chain ID:", (await ethers.provider.getNetwork()).chainId.toString());

  console.log("\n=== Mint calldata ===");
  const mintSelector = "0x1249c58b"; // keccak256("mint()")[0:4]
  console.log("mint() selector:", mintSelector);
  console.log("\nTo mint via OKX Agentic Wallet CLI:");
  console.log(`  onchainos wallet contract-call \\`);
  console.log(`    --to ${address} \\`);
  console.log(`    --chain 196 \\`);
  console.log(`    --input-data ${mintSelector}`);

  // Save deployment info
  const fs = require("fs");
  const deploymentInfo = {
    contract: "AgenticNFT",
    address,
    deployer: deployer.address,
    network: "xlayer",
    chainId: 196,
    mintSelector,
    deployedAt: new Date().toISOString(),
  };
  fs.writeFileSync(
    "./deployments/xlayer.json",
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\nDeployment info saved to ./deployments/xlayer.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
