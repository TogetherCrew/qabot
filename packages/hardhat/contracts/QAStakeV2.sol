// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.9;

import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

import {QABot} from "./QABot.sol";
import {QAStake} from "./QAStake.sol";

error QAStake__AmountLessOrEqualZero();
error QAStake__TransferFailed();
error QAStake__AmountGreaterThanBalance();

/// @custom:security-contact felipe.novaes.rocha@gmail.com
contract QAStakeV2 is QAStake {
    uint256 public version = 2;
    QABot public botToken2;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initializeV2(QABot _botToken2) public reinitializer(2) {
        __Pausable_init();
        __AccessControl_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(UPGRADER_ROLE, msg.sender);

        version = 2;
        botToken2 = _botToken2;
    }

    function _authorizeUpgrade(address newImplementation) internal virtual override onlyRole(UPGRADER_ROLE) {}
}
