import { ethers } from "ethers";
import { readFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Load artifact
const artifact = JSON.parse(
  readFileSync(path.join(__dirname, "../artifacts/contracts/AgenticNFT.sol/AgenticNFT.json"), "utf8")
);

// Contract constructor args
const NAME = "AgenticNFT";
const SYMBOL = "ANFT";
const BASE_URI = "ipfs://bafybeig6xv5nwphfmvcnektpnojts5lgv5zs7yby7v4wdwkuqxq5bveamm/";

// ABI-encode constructor arguments
const abiCoder = ethers.AbiCoder.defaultAbiCoder();
const constructorArgs = abiCoder.encode(
  ["string", "string", "string"],
  [NAME, SYMBOL, BASE_URI]
);

// initCode = bytecode + encoded constructor args
const initCode = artifact.bytecode + constructorArgs.slice(2); // remove 0x prefix from args

// Salt — deterministic, easy to reproduce
const salt = "0x" + "00".repeat(31) + "01"; // 0x0000...0001

// Compute CREATE2 address
// CREATE2 address = keccak256(0xff ++ factory ++ salt ++ keccak256(initCode))[12:]
const FACTORY = "0x4e59b44847b379578588920cA78FbF26c0B4956C";
const create2Address = ethers.getCreate2Address(
  FACTORY,
  salt,
  ethers.keccak256(initCode)
);

// The CREATE2 factory calldata is simply: salt (32 bytes) + initCode
// The factory function: fallback() receives `salt ++ initCode` as calldata
const calldata = salt + initCode.slice(2); // remove 0x from initCode, keep from salt

console.log("=== AgenticNFT CREATE2 Deployment ===\n");
console.log("Factory:         ", FACTORY);
console.log("Salt:            ", salt);
console.log("Constructor args:");
console.log("  name:          ", NAME);
console.log("  symbol:        ", SYMBOL);
console.log("  baseTokenURI:  ", BASE_URI);
console.log("\nPredicted address:", create2Address);
console.log("\nInitCode length: ", initCode.length / 2 - 1, "bytes");
console.log("Calldata length: ", calldata.length / 2 - 1, "bytes");
console.log("\n=== Mint Command (after deployment) ===");
console.log(`onchainos wallet contract-call --to ${create2Address} --chain 196 --input-data 0x1249c58b`);
console.log("\n=== Deploy Command ===");
console.log(`onchainos wallet contract-call \\`);
console.log(`  --to ${FACTORY} \\`);
console.log(`  --chain 196 \\`);
console.log(`  --input-data ${calldata}`);

// Write to deployment info
import { writeFileSync, mkdirSync, existsSync } from "fs";
const deploymentsDir = path.join(__dirname, "../deployments");
if (!existsSync(deploymentsDir)) mkdirSync(deploymentsDir);

const deployInfo = {
  contract: "AgenticNFT",
  address: create2Address,
  factory: FACTORY,
  salt,
  deployer: "onchainos-agentic-wallet",
  network: "xlayer",
  chainId: 196,
  mintSelector: "0x1249c58b",
  constructorArgs: { name: NAME, symbol: SYMBOL, baseTokenURI: BASE_URI },
  calldata,
  status: "pending",
  note: "Deploy via: onchainos wallet contract-call --to FACTORY --chain 196 --input-data CALLDATA"
};

writeFileSync(
  path.join(deploymentsDir, "xlayer-create2.json"),
  JSON.stringify(deployInfo, null, 2)
);
console.log("\nDeployment info written to deployments/xlayer-create2.json");
