import { defaultAPIEndpoint } from '@constants/auth';
import { StoreSlice } from './store';

export interface ContractSlice {
  botTokens?: bigint | undefined;
  stakedTokens?: bigint | undefined;
  setBotTokens: (botTokens: bigint | undefined) => void;
  setStakedTokens: (stakedTokens: bigint | undefined) => void;
}

export const createContractSlice: StoreSlice<ContractSlice> = (set, get) => ({
  botTokens: undefined,
  stakedTokens: undefined,
  setBotTokens: (botTokens: bigint | undefined) => {
    set((prev: ContractSlice) => ({
      ...prev,
      botTokens: botTokens,
    }));
  },
  setStakedTokens: (stakedTokens: bigint | undefined) => {
    set((prev: ContractSlice) => ({
      ...prev,
      stakedTokens: stakedTokens,
    }));
  },
});
