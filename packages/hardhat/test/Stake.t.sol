// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test} from "forge-std/Test.sol";
import {QABot} from "../contracts/QABot.sol";
import {QAStake} from "../contracts/QAStake.sol";

import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

contract QAStakeTest is Test {
    QABot public token;
    QAStake public stake;
    ERC1967Proxy public tokenProxy;

    function setUp() public {
        // address me = address(1);
        // vm.startPrank(me);
        token = new QABot();
        tokenProxy = new ERC1967Proxy(address(token), abi.encodeWithSelector(token.initialize.selector));
        token = QABot(address(tokenProxy));
        token.mint(address(this), 1000);
        stake = new QAStake(token);
        // vm.stopPrank();
    }

    function testStake() public {
        uint256 AMOUNT_TO_STAKE = 500;
        token.approve(address(stake), AMOUNT_TO_STAKE);
        stake.stake(AMOUNT_TO_STAKE);
    }
}
