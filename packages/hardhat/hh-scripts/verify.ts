import { ethers, upgrades } from "hardhat";
import hre from "hardhat";

async function main() {
  const contractName = "QABot";

  console.log(`Verifiying... on network: ${hre.network.name}`);

  const contractFullyQualifedName = `contracts/${contractName}.sol:${contractName}`;

  const constructorArgs: any[] = [];

  console.log("constructorArgs", constructorArgs);

  const result = await hre.run("verify:verify", {
    address: "0x7dfc9f640a6b7b22bb474c9802f89c687ceecbe8",
    contract: contractFullyQualifedName,
    constructorArguments: constructorArgs,
  });
  console.log("result", result);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
