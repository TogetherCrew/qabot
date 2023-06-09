// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test} from "forge-std/Test.sol";
import {QABot} from "../contracts/QABot.sol";
import {QAStake} from "../contracts/QAStake.sol";
import {QAStakeV2} from "../contracts/QAStakeV2.sol";

import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

contract QAStakeTest is Test {
    QABot public token;
    QAStake public stake;
    ERC1967Proxy public tokenProxy;

    function setUp() public {
        token = new QABot();
        tokenProxy = new ERC1967Proxy(address(token), abi.encodeWithSelector(token.initialize.selector));
        token = QABot(address(tokenProxy));
        token.mint(address(this), 1000);

        stake = new QAStake();

        ERC1967Proxy proxy = new ERC1967Proxy(address(stake), abi.encodeWithSelector(stake.initialize.selector, token));
        stake = QAStake(address(proxy));
    }

    function testStakeAndUnstake() public {
        uint256 AMOUNT_TO_STAKE = 500;
        token.approve(address(stake), AMOUNT_TO_STAKE);
        stake.stake(AMOUNT_TO_STAKE);
        assertEq(stake.balances(address(this)), AMOUNT_TO_STAKE);
        stake.unstake(AMOUNT_TO_STAKE);
        assertEq(stake.balances(address(this)), 0);
    }

    function testUpgradeV2() public {
        QAStakeV2 stakeV2 = new QAStakeV2();

        stake.upgradeToAndCall(
            address(stakeV2), abi.encodeWithSelector(stakeV2.initializeV2.selector, QABot(address(0x1)))
        );
        assertEq(QAStakeV2(address(stake)).version(), 2);
    }
}
