import React from 'react';

import useStore from '@store/store';

import CalculatorIcon from '@icon/CalculatorIcon';
import { formatEther } from 'viem';

export const Balances = () => {
  const botTokens = useStore((state) => state.botTokens);
  const stakedTokens = useStore((state) => state.stakedTokens);

  return (
    <>
      <a className='flex py-2 px-2 items-center gap-3 rounded-md hover:bg-gray-500/10 transition-colors duration-200 text-white text-sm'>
        <CalculatorIcon />
        {`BOT ${formatEther(botTokens ?? 0n)}`}
      </a>
      <a className='flex py-2 px-2 items-center gap-3 rounded-md hover:bg-gray-500/10 transition-colors duration-200 text-white text-sm'>
        <CalculatorIcon />
        {`sBOT ${formatEther(stakedTokens ?? 0n)}`}
      </a>
    </>
  );
};

export default Balances;
