import { ethers, upgrades } from "hardhat";
import hre from "hardhat";

async function main() {
  const contractName = "QABot";

  const ContractFactory = await ethers.getContractFactory(contractName);

  const instance = await upgrades.deployProxy(ContractFactory);
  console.log(`deployProxy`);
  await instance.deployed();
  console.log(`deployed`);

  // console.log(`Proxy deployed to ${instance.address}`);
  console.log(`Proxy deployed to ${instance.address}`);

  const IMPL_SLOT =
    "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc";

  let implementationAddress = await ethers.provider.getStorageAt(
    instance.address,
    // "0x098FeAFa9D8C7a932655D724406b7AF33368b8a7",
    IMPL_SLOT
  );

  implementationAddress = implementationAddress.slice(26);
  implementationAddress = "0x" + implementationAddress;

  console.log(`Implementation deployed to ${implementationAddress}`);

  console.log(`Verifiying... on network: ${hre.network.name}`);

  const contractFullyQualifedName = `contracts/${contractName}.sol:${contractName}`;

  const constructorArgs: any[] = [];

  console.log("constructorArgs", constructorArgs);

  const result = await hre.run("verify:verify", {
    address: implementationAddress,
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
