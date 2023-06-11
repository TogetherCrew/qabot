// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.9;

import {QABot} from "./QABot.sol";

import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

error QAStake__AmountLessOrEqualZero(); // 98550d0b  =>  QAStake__AmountLessOrEqualZero()
error QAStake__TransferFailed(); // 538bb501  =>  QAStake__TransferFailed()
error QAStake__AmountGreaterThanBalance(); // e4ab3929 =>  QAStake__AmountGreaterThanBalance()

/// @custom:security-contact felipe.novaes.rocha@gmail.com
contract QAStake is Initializable, PausableUpgradeable, AccessControlUpgradeable, UUPSUpgradeable {
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");
    bytes32 public constant CHARGER_ROLE = keccak256("CHARGER_ROLE");

    QABot internal botToken;

    mapping(address => uint256) public balances;

    event Staked(address who, uint256 amount);
    event Unstaked(address who, uint256 amount);
    event Charged(address who, uint256 amount);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(QABot _botToken) public initializer {
        __Pausable_init();
        __AccessControl_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(UPGRADER_ROLE, msg.sender);
        _grantRole(CHARGER_ROLE, msg.sender);
        botToken = _botToken;
    }

    function pause() public onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() public onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    function _authorizeUpgrade(address newImplementation) internal virtual override onlyRole(UPGRADER_ROLE) {}

    modifier onlyAmountGTEqZero(uint256 _amount) {
        if (_amount <= 0) {
            revert QAStake__AmountLessOrEqualZero();
        }
        _;
    }

    function stake(uint256 _amount) external onlyAmountGTEqZero(_amount) {
        balances[msg.sender] += _amount;

        bool transferSuccess = botToken.transferFrom(msg.sender, address(this), _amount);
        if (!transferSuccess) {
            revert QAStake__TransferFailed();
        }

        emit Staked(msg.sender, _amount);
    }

    function unstake(uint256 _amount) external onlyAmountGTEqZero(_amount) {
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

    function charge(address from, uint256 _amount) external onlyAmountGTEqZero(_amount) onlyRole(CHARGER_ROLE) {
        if (_amount > balances[from]) {
            revert QAStake__AmountGreaterThanBalance();
        }

        balances[from] -= _amount;

        emit Charged(from, _amount);
    }
}
