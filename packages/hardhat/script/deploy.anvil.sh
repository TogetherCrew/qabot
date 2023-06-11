# source .env
# forge script scripts/deploy.anvil.s.sol:DeployAnvil \
#     -f http://127.0.0.1:8545 \
#     --broadcast
forge script script/deploy.anvil.s.sol:DeployAnvil \
    -f http://127.0.0.1:8545 \
    --broadcast


# cast send "0xcbEAF3BDe82155F56486Fb5a1072cb8baAf547cc" "mint(address,uint256)" "0x3CeeF2C35d55a61514CeCe32C165fB96536d76c4" "1000000000000000000000" --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80