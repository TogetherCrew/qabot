import React, { useEffect, useState } from 'react';
import useStore from '@store/store';

import ChatContent from './ChatContent';
import MobileBar from '../MobileBar';
import StopGeneratingButton from '@components/StopGeneratingButton/StopGeneratingButton';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAccount, useNetwork, erc20ABI } from 'wagmi';
import { readContract, watchContractEvent, signMessage } from 'wagmi/actions';
import { SiweMessage } from 'siwe';
import { isExpired, decodeToken } from 'react-jwt';
import { formatEther } from 'viem';
import { AccessTokenStatus } from '@store/auth-slice';
import { CONTRACT_ADDRESSES, abiStake, abiToken } from '@utils/contract';

const SIGNATURE_KEY = 'signature';
const ACCESS_TOKEN_KEY = 'access_token';
const STATEMENT_MSG = 'Sign in with Ethereum to the QABot App.';

const Chat = () => {
  const hideSideMenu = useStore((state) => state.hideSideMenu);
  const setAccessToken = useStore((state) => state.setAccessToken);
  const accessToken = useStore((state) => state.accessToken);

  const statusAccessToken = useStore((state) => state.status);
  const setStatusAccessToken = useStore((state) => state.setStatus);

  const botTokens = useStore((state) => state.botTokens);
  const setBotTokens = useStore((state) => state.setBotTokens);

  const stakedTokens = useStore((state) => state.stakedTokens);
  const setStakedTokens = useStore((state) => state.setStakedTokens);

  const { address, isConnected, connector } = useAccount();

  const [state, setState] = useState<{
    address?: string;
    error?: Error;
    isLoading?: boolean;
  }>({});

  const [_message, setMessage] = useState<SiweMessage>();
  const [_signature, setSignature] = useState<string | undefined>();

  const { chain } = useNetwork();

  const readBalanceToken = async (_address: `0x${string}`) => {
    const data = await readContract({
      address: CONTRACT_ADDRESSES.QABotProxy as `0x${string}`,
      abi: erc20ABI,
      functionName: 'balanceOf',
      args: [_address ?? '0x'],
    });
    console.log('balance:', data);
    setBotTokens(data);
  };
  const readBalanceStaked = async (_address: `0x${string}`) => {
    const data = await readContract({
      address: CONTRACT_ADDRESSES.QAStakeProxy as `0x${string}`,
      abi: abiStake,
      functionName: 'balances',
      args: [_address ?? '0x'],
    });
    console.log('Staked Balance:', data);
    setStakedTokens(data as bigint);
  };

  useEffect(() => {
    const unwatchStake = watchContractEvent(
      {
        address: CONTRACT_ADDRESSES.QAStakeProxy as `0x${string}`,
        abi: abiStake,
        eventName: 'Staked',
      },
      (logs) => {
        console.log('logs', logs);
        const log: any = logs[0];
        if (log?.args?.who === address && address) {
          readBalanceStaked(address);
        } else {
          console.log('logs', logs);
        }
      }
    );

    const unwatchToken = watchContractEvent(
      {
        address: CONTRACT_ADDRESSES.QABotProxy as `0x${string}`,
        abi: abiToken,
        eventName: 'Transfer',
      },
      (logs) => {
        const log: any = logs[0];
        if (log?.args?.to === address && address) {
          readBalanceToken(address);
        } else {
          console.log('logs', logs);
        }
      }
    );

    if (isConnected && address && connector) {
      const _accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
      setAccessToken(_accessToken);
      console.log('calling readContract');
      // use wagmi to call balanceOf a ERC20 token
      readBalanceToken(address);
      readBalanceStaked(address);
    }

    return () => {
      unwatchStake();
      unwatchToken();
    };
  }, [address, isConnected, connector]);

  useEffect(() => {
    const run = async () => {
      console.log('Storage:accessToken', accessToken);
      if (accessToken) {
        const decodedToken = decodeToken(accessToken);
        if (isExpired(accessToken)) {
          console.log('token is expired');
          setStatusAccessToken(AccessTokenStatus.EXPIRED);
          setAccessToken(undefined);
          localStorage.removeItem(ACCESS_TOKEN_KEY);
          // do signin process
          await signIn();
        } else if (decodedToken) {
          console.log('token is valid');
          // means token is valid and not expired

          setAccessToken(accessToken);
          setStatusAccessToken(AccessTokenStatus.LOGGED);
        } else {
          setStatusAccessToken(AccessTokenStatus.NOT_LOGGED_IN);
          setAccessToken(undefined);
          localStorage.removeItem(ACCESS_TOKEN_KEY);
          console.log('token is invalid');
          // means token is invalid
          await signIn();
        }
        // if (!isLogged) {
        //   updateAccessToken(accessToken);
        // }
      } else {
        console.log('no token');
        setStatusAccessToken(AccessTokenStatus.NOT_LOGGED_IN);
        await signIn();
      }
    };
    run().catch(console.error);
  }, [accessToken]);

  const updateAccessToken = async (token: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
    setAccessToken(token);
  };
  const signIn = async () => {
    try {
      // Validation
      const chainId = chain?.id;
      console.log('address', address);

      if (
        !address ||
        !chainId ||
        statusAccessToken === AccessTokenStatus.LOGGED ||
        statusAccessToken === AccessTokenStatus.LOGGING
      ) {
        console.log('statusAccessToken', statusAccessToken);
        console.log('no address or chainId or already logged in');
        return;
      }
      setStatusAccessToken(AccessTokenStatus.LOGGING);
      // Set loading
      setState({
        ...state,
        error: undefined,
        isLoading: true,
      });

      // Retrieve nonce data
      // const nonceResult = await fetch(
      //   `${import.meta.env.VITE_API_URL}/auth/nonce`,
      //   {
      //     method: 'get',
      //     credentials: 'include',
      //   }
      // );
      //const nonceJson =   await nonceResult.json();
      const now = new Date().toISOString();
      // add 15 minutes
      const expirationTime = new Date(
        new Date().getTime() + 15 * 60000
      ).toISOString();

      const nonceJson = {
        data: {
          nonce: '234327',
          expirationTime: expirationTime,
        },
      };

      console.log('nonceJson', nonceJson);

      // Configure message
      const message = new SiweMessage({
        domain: window.location.host,
        address,
        statement: STATEMENT_MSG,
        uri: window.location.origin,
        version: '1',
        chainId,
        // nonce: nonceJson.data.nonce,
        // issuedAt: nonceJson.data.issuedAt,
        expirationTime: nonceJson.data.expirationTime,
      });

      setMessage(message);

      const msgPrepared = message.prepareMessage();
      console.log('messageStr', JSON.stringify(msgPrepared));
      // Prompt for signature

      try {
        const signResult = await signMessage({ message: msgPrepared });
        // /Generate token
        const res = await fetch(`${import.meta.env.VITE_API_URL}/token`, {
          method: 'post',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message_eip4361_str: msgPrepared,
            signature: signResult,
          }),
          // credentials: 'include',
        });
        if (res.ok) {
          const json = await res.json();
          console.log('json', json);
          if ('access_token' in json) {
            setStatusAccessToken(AccessTokenStatus.LOGGED);
            updateAccessToken(json.access_token);
          }
        }

        console.log('signResult', signResult);
        setSignature(signResult);

        // store signature in local storage
        localStorage.setItem(SIGNATURE_KEY, signResult);
        // Reset loading state
        setState({
          ...state,
          isLoading: false,
        });
      } catch (error) {
        console.log('error', error);
        setStatusAccessToken(AccessTokenStatus.NOT_LOGGED_IN);
        setState({
          ...state,
          error: error as Error,
          isLoading: false,
        });
      }
    } catch (error) {
      setState({
        ...state,
        error: error as Error,
        isLoading: false,
      });
    }
  };

  return (
    <div
      className={`flex h-full flex-1 flex-col ${
        hideSideMenu ? 'md:pl-0' : 'md:pl-[260px]'
      }`}
    >
      <ConnectButton />
      {isConnected && statusAccessToken === AccessTokenStatus.LOGGED && (
        <div className='flex flex-col items-center justify-center h-full text-white'>
          <div className='text-2xl font-bold'>Welcome</div>
          <>
            {botTokens && (
              <>
                <div className='text-1xl font-bold'>Your balance</div>
                <div className='text-xl'>$BOT:{formatEther(botTokens)}</div>
              </>
            )}
            {stakedTokens && (
              <>
                <div className='text-1xl font-bold'>Your balance</div>
                <div className='text-xl'>
                  Staked BOTs:{formatEther(stakedTokens)}
                </div>
              </>
            )}
          </>
        </div>
      )}
      <MobileBar />
      <main className='relative h-full w-full transition-width flex flex-col overflow-hidden items-stretch flex-1'>
        <ChatContent />
        <StopGeneratingButton />
      </main>
    </div>
  );
};

export default Chat;
