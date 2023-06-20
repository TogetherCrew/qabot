import CONTRACT_ADDRESSES from '@src/../../hardhat/addresses.json';
import { readContract, signTypedData } from 'wagmi/actions';

export { abi as abiStake } from '@src/../../hardhat/artifacts-foundry/QAStake.sol/QAStake.json';
import { abi as abiToken } from '@src/../../hardhat/artifacts-foundry/QABot.sol/QABot.json';
import { parseEther } from 'viem';

export const PERMIT_TYPE_STRUCT = {
  Permit: [
    {
      name: 'owner',
      type: 'address',
    },
    {
      name: 'spender',
      type: 'address',
    },
    {
      name: 'value',
      type: 'uint256',
    },
    {
      name: 'nonce',
      type: 'uint256',
    },
    {
      name: 'deadline',
      type: 'uint256',
    },
  ],
};

export async function signPermit(
  address: string,
  chainId: number,
  currentBotTokens: number,
  additionalDeadlineSecs: number
) {
  const tokenAddr = CONTRACT_ADDRESSES.QABotProxy as `0x${string}`;

  const nonce = (await readContract({
    address: tokenAddr,
    abi: abiToken,
    functionName: 'nonces',
    args: [address],
  })) as bigint;

  const name = (await readContract({
    address: tokenAddr,
    abi: abiToken,
    functionName: 'name',
  })) as string;

  console.log('nonce', nonce);
  console.log('name', name);

  const values = {
    nonce: nonce,
    owner: address,
    spender: CONTRACT_ADDRESSES.QAStakeProxy as `0x${string}`,
    value: parseEther(currentBotTokens.toString() as `${number}`),
    deadline: BigInt(Math.floor(Date.now() / 1000) + additionalDeadlineSecs),
  };

  const signPermit = await signTypedData({
    domain: {
      name: name ?? 'QABot',
      version: '1',
      chainId: chainId,
      verifyingContract: tokenAddr,
    },
    types: PERMIT_TYPE_STRUCT,
    primaryType: 'Permit',
    message: values,
  });

  console.log('signPermit', signPermit);
}

export { CONTRACT_ADDRESSES };
export { abiToken };
