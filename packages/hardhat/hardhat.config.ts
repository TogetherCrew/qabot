import "dotenv/config";

import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "@openzeppelin/hardhat-upgrades";

// import "@nomiclabs/hardhat-etherscan";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.9",
    settings: {
      optimizer: {
        enabled: true,
      },
    },
  },

  networks: {
    // gnosis: {
    //   url: "https://rpc.gnosischain.com",
    //   chainId: 100,
    //   // accounts: [process.env.PK!],
    // },
    mumbai: {
      url: "https://polygon-mumbai-bor.publicnode.com",
      chainId: 80001,
      // accounts: [process.env.PK!],
    },
    matic: {
      url: "https://polygon.llamarpc.com",
      chainId: 137,
      // accounts: [process.env.PK!],
    },
  },
  // typechain: {
  //   alwaysGenerateOverloads: true,
  // },
  etherscan: {
    // Your API key for Etherscan
    // Obtain one at https://etherscan.io/
    apiKey: {
      gnosis: process.env.GNOSISSCAN_API_KEY!,
    },
  },
};

export default config;
