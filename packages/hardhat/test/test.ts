import { expect } from "chai";
import { ethers, upgrades } from "hardhat";

describe("QABot", function () {
  it("Test contract", async function () {
    const ContractFactory = await ethers.getContractFactory("QABot");

    const instance = await upgrades.deployProxy(ContractFactory);
    await instance.deployed();

    expect(await instance.name()).to.equal("QABot");
  });
});
