// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract TransactionGateway is AccessControl, ReentrancyGuard {

    bytes32 public constant BACKEND_ROLE = keccak256("BACKEND_ROLE");

    IERC20 public usdc;
    IERC20 public token;
    address public vaultWallet;
    address public tokenWallet;

    struct DepositInfo {
        uint256 amount;
        address sender;
        bool    exists;
    }

    mapping(bytes32 => DepositInfo) public deposits;

    event StableDeposited(address indexed user, uint256 amount, bytes32 depositID);
    event ETFDeposited(address indexed user, uint256 tokenAmount, bytes32 depositID);

    constructor(address _usdc, address _token, address _vaultWallet, address _tokenWallet) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        usdc = IERC20(_usdc);
        token = IERC20(_token);
        vaultWallet = _vaultWallet;
        tokenWallet = _tokenWallet;
    }

    function depositUSDC(uint256 amount, bytes32 frontendHash) external nonReentrant {
        require(amount > 0, "Amount must be greater than 0");
        require(usdc.transferFrom(msg.sender, vaultWallet, amount), "USDC transfer failed");
        
        // uint256 timestamp = block.timestamp;
        // bytes32 depositID = keccak256(abi.encodePacked(msg.sender, amount, timestamp));

        deposits[frontendHash] = DepositInfo(amount, msg.sender, true);

        emit StableDeposited(msg.sender, amount, frontendHash);
    }

    function depositOurToken(uint256 tokenAmount, bytes32 frontendHash) external nonReentrant {
        require(tokenAmount > 0, "Amount must be greater than 0");
        require(token.transferFrom(msg.sender, tokenWallet, tokenAmount), "Token transfer failed");

        // uint256 timestamp = block.timestamp;
        // bytes32 depositID = keccak256(abi.encodePacked(msg.sender, tokenAmount, timestamp));


        deposits[frontendHash] = DepositInfo(tokenAmount, msg.sender, true);

        emit ETFDeposited(msg.sender, tokenAmount, frontendHash);
    }
}

