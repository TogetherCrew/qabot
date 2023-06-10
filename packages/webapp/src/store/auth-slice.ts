import { defaultAPIEndpoint } from '@constants/auth';
import { StoreSlice } from './store';

export enum AccessTokenStatus {
  NOT_LOGGED_IN,
  LOGGED_IN,
  EXPIRED,
}

export interface AuthWalletSlice {
  accessToken?: string | undefined | null;
  address?: string | undefined;
  status: AccessTokenStatus;
  setAccessToken: (accessToken: string | undefined | null) => void;
  setAddress: (address: string) => void;
  setStatus: (status: AccessTokenStatus) => void;
}

export interface AuthSlice {
  apiKey?: string;
  apiEndpoint: string;
  firstVisit: boolean;
  setApiKey: (apiKey: string) => void;
  setApiEndpoint: (apiEndpoint: string) => void;
  setFirstVisit: (firstVisit: boolean) => void;
}

export const createAuthSlice: StoreSlice<AuthSlice> = (set, get) => ({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY || undefined,
  apiEndpoint: defaultAPIEndpoint,
  firstVisit: true,
  setApiKey: (apiKey: string) => {
    set((prev: AuthSlice) => ({
      ...prev,
      apiKey: apiKey,
    }));
  },
  setApiEndpoint: (apiEndpoint: string) => {
    set((prev: AuthSlice) => ({
      ...prev,
      apiEndpoint: apiEndpoint,
    }));
  },
  setFirstVisit: (firstVisit: boolean) => {
    set((prev: AuthSlice) => ({
      ...prev,
      firstVisit: firstVisit,
    }));
  },
});

export const createAuthWalletSlice: StoreSlice<AuthWalletSlice> = (
  set,
  get
) => ({
  accessToken: undefined,
  address: undefined,
  status: AccessTokenStatus.NOT_LOGGED_IN,
  setAccessToken: (accessToken: string | undefined | null) => {
    set((prev: AuthWalletSlice) => ({
      ...prev,
      accessToken: accessToken,
    }));
  },
  setAddress: (address: string) => {
    set((prev: AuthWalletSlice) => ({
      ...prev,
      address: address,
    }));
  },
  setStatus: (status: AccessTokenStatus) => {
    set((prev: AuthWalletSlice) => ({
      ...prev,
      status: status,
    }));
  },
});
