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

  // const contractFullyQualifedName = `contracts/${contractName}.sol:${contractName}`;

  // console.log("hre", hre.network.name);

  // const constructorArgs: any[] = [];

  // console.log("constructorArgs", constructorArgs);

  // const result = await hre.run("verify:verify", {
  //   address: instance.address,
  //   contract: contractFullyQualifedName,
  //   constructorArguments: constructorArgs,
  // });
  // console.log("result", result);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
