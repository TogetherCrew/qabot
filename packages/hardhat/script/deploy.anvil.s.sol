// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "forge-std/Script.sol";
import "forge-std/console.sol";

import {QABot} from "../contracts/QABot.sol";
import {QAStake} from "../contracts/QAStake.sol";
import {QAStakeV2} from "../contracts/QAStakeV2.sol";

import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

contract DeployAnvil is Script {
    function run() external {
        // vm.startBroadcast(vm.envUint("PK"));
        vm.startBroadcast(0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80);

        QABot token = new QABot();
        ERC1967Proxy tokenProxy = new ERC1967Proxy(address(token), abi.encodeWithSelector(token.initialize.selector));
        token = QABot(address(tokenProxy));
        token.mint(address(0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266), 1000 ether);

        QAStake stake = new QAStake();
        ERC1967Proxy proxy = new ERC1967Proxy(address(stake), abi.encodeWithSelector(stake.initialize.selector, token));
        stake = QAStake(address(proxy));

        console.log("TOKEN_CONTRACT_ADDRESS=", address(token));
        console.log("STAKE_CONTRACT_ADDRESS=", address(stake));

        token.approve(address(stake), 1000 ether);
        stake.stake(1000 ether);

        vm.stopBroadcast();
    }
}
