import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import useStore from '@store/store';

import PopupModal from '@components/PopupModal';

import { EtherInput } from '@components/Input/EtherInput';
import { formatEther, parseEther } from 'viem';
import { writeContract } from 'wagmi/actions';

import { CONTRACT_ADDRESSES, abiStake, abiToken } from '@utils/contract';
import { useAccount, useChainId } from 'wagmi';

const ADDITIONAL_DEADLINE_IN_SECS = 60 * 60 * 24 * 7; // 7 days

const StakeMenu = ({
  setIsModalOpen,
}: {
  setIsModalOpen: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
  const { t } = useTranslation(['main', 'api']);

  const botTokens = useStore((state) => state.botTokens);
  // const setBotTokens = useStore((state) => state.setBotTokens);

  const stakedTokens = useStore((state) => state.stakedTokens);
  // const setStakedTokens = useStore((state) => state.setStakedTokens);

  const [currentBotTokens, setCurrentBotTokens] = useState<bigint | string>(
    botTokens ?? 0n
  );
  const [currentStakedTokens, setCurrentStakedTokens] = useState<bigint>(
    stakedTokens ?? 0n
  );

  const chainId = useChainId();
  const { address } = useAccount();

  const handleSave = async () => {
    if (!address) {
      console.log('no address');
      return;
    }
    console.log('chainId', chainId);

    const tokenTx = await writeContract({
      address: CONTRACT_ADDRESSES.QABotProxy as `0x${string}`,
      abi: abiToken,
      functionName: 'approve',
      args: [
        CONTRACT_ADDRESSES.QAStakeProxy as `0x${string}`,
        parseEther(currentBotTokens.toString() as `${number}`),
      ],
    });
    console.log('tokenTx', tokenTx);

    const stakeTx = await writeContract({
      address: CONTRACT_ADDRESSES.QAStakeProxy as `0x${string}`,
      abi: abiStake,
      functionName: 'stake',
      args: [parseEther(currentBotTokens.toString() as `${number}`)],
    });
    console.log('stakeTx', stakeTx);
    setIsModalOpen(false);
  };

  return (
    <PopupModal
      title={t('stake') as string}
      setIsModalOpen={setIsModalOpen}
      handleConfirm={handleSave}
    >
      <div className='p-6 border-b border-gray-200 dark:border-gray-600'>
        <div className='flex gap-2 items-center justify-center mt-2'>
          <div className='text-gray-900 dark:text-gray-300 text-sm'>
            {'Current BOT tokens:'}
          </div>
          <div className='text-gray-900 dark:text-gray-300 text-sm'>
            <>{botTokens && formatEther(botTokens)}</>
          </div>
        </div>

        <div className='flex gap-2 items-center justify-center mt-2'>
          <div className='text-gray-900 dark:text-gray-300 text-sm'>
            {'How much to Stake?'}
          </div>
          <div>
            <EtherInput
              value={currentBotTokens.toString()}
              name='stake'
              onChange={(e: any) => {
                console.log('e', e);
                console.log('_botTokens', botTokens);
                if (botTokens) {
                  const parts = e.split('.');
                  if (parts.length <= 2) {
                  } else {
                    e = e.replace('.', '');
                  }
                  if (parts[0] <= botTokens) {
                    setCurrentBotTokens(e);
                  } else {
                    alert(
                      'You do not have enough BOT tokens to stake this amount'
                    );
                  }
                }
              }}
              placeholder='0.0'
            />
          </div>
        </div>

        <div className='text-gray-900 dark:text-gray-300 text-sm flex flex-col gap-3 leading-relaxed'>
          <div className='flex gap-3 items-center justify-center h-full'>
            <p className='mt-4'>{'Current Staked: '}</p>
            <div className='text-sm font-medium flex-grow h-8 items-center'>
              <>{formatEther(currentStakedTokens)}</>
            </div>
          </div>
        </div>
      </div>
    </PopupModal>
  );
};

export default StakeMenu;
