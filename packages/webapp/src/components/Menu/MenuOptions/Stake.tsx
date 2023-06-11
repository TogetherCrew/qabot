import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import MoneyIcon from '@icon/MoneyIcon';
import ApiMenu from '@components/ApiMenu';
import StakeMenu from '@components/StakeMenu/StakeMenu';

const Config = () => {
  const { t } = useTranslation();
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  return (
    <>
      <a
        className='flex py-2 px-2 items-center gap-3 rounded-md hover:bg-gray-500/10 transition-colors duration-200 text-white cursor-pointer text-sm'
        id='api-menu'
        onClick={() => setIsModalOpen(true)}
      >
        <MoneyIcon />
        {'Stake'}
      </a>
      {isModalOpen && <StakeMenu setIsModalOpen={setIsModalOpen} />}
    </>
  );
};

export default Config;
