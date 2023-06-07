// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.9;

import {QABot} from "./QABot.sol";

error QAStake__AmountLessOrEqualZero();
error QAStake__TransferFailed();
error QAStake__AmountGreaterThanBalance();

contract QAStake {
    QABot public immutable botToken;

    mapping(address => uint256) public balances;

    event Staked(address who, uint256 amount);
    event Unstaked(address who, uint256 amount);

    constructor(QABot _botToken) {
        botToken = _botToken;
    }

    function stake(uint256 _amount) external {
        if (_amount <= 0) {
            revert QAStake__AmountLessOrEqualZero();
        }

        balances[msg.sender] += _amount;

        bool transferSuccess = botToken.transferFrom(msg.sender, address(this), _amount);
        if (!transferSuccess) {
            revert QAStake__TransferFailed();
        }

        emit Staked(msg.sender, _amount);
    }

    function unstake(uint256 _amount) external {
        if (_amount <= 0) {
            revert QAStake__AmountLessOrEqualZero();
        }
        if (_amount > balances[msg.sender]) {
            revert QAStake__AmountGreaterThanBalance();
        }

        balances[msg.sender] -= _amount;

        bool transferSuccess = botToken.transfer(msg.sender, _amount);
        if (!transferSuccess) {
            revert QAStake__TransferFailed();
        }

        emit Unstaked(msg.sender, _amount);
    }
}
