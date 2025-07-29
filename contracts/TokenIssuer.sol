// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";


interface ITransactionGateway {
    function deposits(bytes32 frontendHash) external view returns (
        uint256 amount,
        address sender,
        bool exists
    );
}

contract TokenIssuer is ERC20, AccessControl, ReentrancyGuard {

    // bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    mapping(bytes32 => bool) public processedTransactions;

    ITransactionGateway public gateway;


    event MintProcessed(address indexed user, uint256 tokenAmount, bytes32 frontendHash);
    event BurnProcessed(address indexed user, uint256 tokenAmount, bytes32 frontendHash);
    event RefundTriggered(bytes32 frontendHash, string reason);

    constructor() ERC20("Digital SPY", "DSPY") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function setGateway(address _gateway) external onlyRole(DEFAULT_ADMIN_ROLE) {
        gateway = ITransactionGateway(_gateway);
    }

    function mint(
        address user,
        uint256 tokenAmount,
        bytes32 frontendHash
    ) external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
        (, address sender, bool exists) = gateway.deposits(frontendHash);
        require(exists, "Deposit not found");
        require(user == sender, "Depositor and receiver are different");
        require(!processedTransactions[frontendHash], "Already processed");
        require(tokenAmount > 0, "Invalid token amount");
        
        processedTransactions[frontendHash] = true;
        _mint(user, tokenAmount);
        emit MintProcessed(user, tokenAmount, frontendHash);
    }

    function burn(
        address user,
        uint256 tokenAmount,
        bytes32 frontendHash
    ) external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
        (, , bool exists) = gateway.deposits(frontendHash);
        require(exists, "Deposit not found");
        require(!processedTransactions[frontendHash], "Already processed");
        require(tokenAmount > 0, "Invalid token amount");
        
        processedTransactions[frontendHash] = true;
        _burn(user, tokenAmount);
        emit BurnProcessed(user, tokenAmount, frontendHash);
    }

    function triggerRefund(bytes32 frontendHash, string calldata reason) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(!processedTransactions[frontendHash], "Already processed");
        processedTransactions[frontendHash] = true;
        emit RefundTriggered(frontendHash, reason);
    }
}

