import { ethers } from "ethers";
import { readFileSync, writeFileSync } from "fs";

const RPC_URL = "https://rpc.xlayer.tech";
const TREASURY = "0xe85cd5681567c6a5d141b9fd1d2ec58c5736ff55";

async function main() {
  const privateKey = process.env.DEPLOYER_PRIVATE_KEY;
  if (!privateKey) throw new Error("Set DEPLOYER_PRIVATE_KEY env var");

  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(privateKey, provider);
  const balance = await provider.getBalance(wallet.address);

  console.log("Deploying AgenticNFT v3 (free mint)");
  console.log("  Deployer:", wallet.address);
  console.log("  Balance: ", ethers.formatEther(balance), "OKB");

  if (balance === 0n) throw new Error("Deployer has no OKB. Fund it first.");

  // Load compiled artifact
  const artifact = JSON.parse(
    readFileSync("./artifacts/contracts/AgenticNFT.sol/AgenticNFT.json", "utf8")
  );

  const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, wallet);

  const name = "Club of Agent";
  const symbol = "COA";
  const baseTokenURI = "https://www.clubofagent.com/metadata/";

  console.log("\nDeploying...");
  const contract = await factory.deploy(name, symbol, baseTokenURI);
  console.log("  Tx hash:", contract.deploymentTransaction().hash);
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("  Deployed to:", address);

  const mintSelector = ethers.id("mint()").slice(0, 10);

  console.log("\nTo mint via OKX Agentic Wallet CLI:");
  console.log(`  onchainos wallet contract-call \\`);
  console.log(`    --to ${address} \\`);
  console.log(`    --chain 196 \\`);
  console.log(`    --input-data ${mintSelector}`);

  const deploymentInfo = {
    contract: "AgenticNFT",
    version: "3.0.0",
    address,
    mintPrice: "FREE",
    maxSupply: 10000,
    network: "xlayer",
    chainId: 196,
    mintSelector,
    deployTx: contract.deploymentTransaction().hash,
    deployedAt: new Date().toISOString(),
  };
  writeFileSync("./deployments/xlayer.json", JSON.stringify(deploymentInfo, null, 2));
  console.log("\nSaved to ./deployments/xlayer.json");
}

main().catch((e) => { console.error(e); process.exit(1); });
