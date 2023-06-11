import React from 'react';
import useStore from '@store/store';

import SettingsMenu from '@components/SettingsMenu';
import CollapseOptions from './CollapseOptions';
import Stake from './Stake';
import Balances from '@components/SettingsMenu/Balances';

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || undefined;

const MenuOptions = () => {
  const hideMenuOptions = useStore((state) => state.hideMenuOptions);
  return (
    <>
      <CollapseOptions />
      <div
        className={`${
          hideMenuOptions ? 'max-h-0' : 'max-h-full'
        } overflow-hidden transition-all`}
      >
        {/* {countTotalTokens && <TotalTokenCostDisplay />} */}
        <Balances />
        {/* {googleClientId && <GoogleSync clientId={googleClientId} />} */}
        {/* <AboutMenu /> */}
        {/* <ImportExportChat /> */}
        {/* <Api /> */}
        {<Stake />}
        <SettingsMenu />
        {/* <Me /> */}
      </div>
    </>
  );
};

export default MenuOptions;
