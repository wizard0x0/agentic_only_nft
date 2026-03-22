import { ethers } from "ethers";
import { readFileSync } from "fs";

const RPC_URL  = "https://rpc.xlayer.tech";
const CONTRACT = "0xF0f2F1f61fC4c8A4cc15a78E41102dC81434BB6f";
const BASE_URI = "https://www.clubofagent.com/metadata/";

async function main() {
  const pk = process.env.DEPLOYER_PRIVATE_KEY;
  if (!pk) throw new Error("Set DEPLOYER_PRIVATE_KEY");

  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet   = new ethers.Wallet(pk, provider);

  const abi = ["function setBaseURI(string calldata newBaseURI) external",
               "function baseURI() external view returns (string memory)"];
  const contract = new ethers.Contract(CONTRACT, abi, wallet);

  console.log("Current baseURI:", await contract.baseURI());
  console.log("Setting to:     ", BASE_URI);

  const tx = await contract.setBaseURI(BASE_URI);
  console.log("Tx hash:", tx.hash);
  await tx.wait();
  console.log("Confirmed. New baseURI:", await contract.baseURI());
}

main().catch(e => { console.error(e); process.exit(1); });
