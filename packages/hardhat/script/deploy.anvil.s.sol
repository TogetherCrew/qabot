// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "../lib/forge-std/src/Script.sol";

import {QABot} from "../contracts/QABot.sol";

contract DeployAnvil is Script {
    function run() external {
        vm.startBroadcast(vm.envUint("PK"));
        QABot bot = new QABot();
        bot.initialize();

        vm.stopBroadcast();
    }
}
