import React, { useEffect, useState } from 'react';
import useStore from '@store/store';

import ChatContent from './ChatContent';
import MobileBar from '../MobileBar';
import StopGeneratingButton from '@components/StopGeneratingButton/StopGeneratingButton';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAccount, useNetwork, useSignMessage, erc20ABI } from 'wagmi';
import { watchReadContract } from 'wagmi/actions';
import { SiweMessage } from 'siwe';
import { isExpired, decodeToken } from 'react-jwt';
import { formatEther } from 'viem';
import { AccessTokenStatus } from '@store/auth-slice';
import { set } from 'lodash';

const SIGNATURE_KEY = 'signature';
const ACCESS_TOKEN_KEY = 'access_token';
const STATEMENT_MSG = 'Sign in with Ethereum to the QABot App.';

const Chat = () => {
  const hideSideMenu = useStore((state) => state.hideSideMenu);
  const setAccessToken = useStore((state) => state.setAccessToken);
  const accessToken = useStore((state) => state.accessToken);

  const statusAccessToken = useStore((state) => state.status);
  const setStatusAccessToken = useStore((state) => state.setStatus);

  const { address, isConnected } = useAccount();

  const [state, setState] = useState<{
    address?: string;
    error?: Error;
    isLoading?: boolean;
  }>({});

  const [_message, setMessage] = useState<SiweMessage>();
  const [_signature, setSignature] = useState<string | undefined>();
  const [botTokens, setBotTokens] = useState<bigint>();
  const { chain } = useNetwork();
  const { signMessageAsync } = useSignMessage();

  useEffect(() => {
    if (isConnected && address) {
      console.log('calling watchReadContract');
      // use wagmi to call balanceOf a ERC20 token
      const unwatch = watchReadContract(
        {
          address: '0x098FeAFa9D8C7a932655D724406b7AF33368b8a7',
          abi: erc20ABI,
          functionName: 'balanceOf',
          args: [address ?? '0x'],
        },
        (data) => {
          console.log('BALANCE:', data);
          setBotTokens(data);
        }
      );
    }
  }, [address, isConnected]);

  useEffect(() => {
    const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);

    console.log('Storage:accessToken', accessToken);
    if (accessToken) {
      const decodedToken = decodeToken(accessToken);
      if (isExpired(accessToken)) {
        console.log('token is expired');
        setStatusAccessToken(AccessTokenStatus.EXPIRED);
        // do signin process
        signIn();
      } else if (decodedToken) {
        console.log('token is valid');
        // means token is valid and not expired

        setAccessToken(accessToken);
        setStatusAccessToken(AccessTokenStatus.LOGGED_IN);
      } else {
        setStatusAccessToken(AccessTokenStatus.NOT_LOGGED_IN);
        console.log('token is invalid');
        // means token is invalid
        signIn();
      }
      // if (!isLogged) {
      //   updateAccessToken(accessToken);
      // }
    }
  }, [setAccessToken]);

  const updateAccessToken = async (token: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
    setAccessToken(token);
    // if (token) {
    //   reEvaluateToken(token);
    // }
  };
  const signIn = async () => {
    try {
      // Validation
      const chainId = chain?.id;
      console.log('address', address);

      if (
        !address ||
        !chainId ||
        statusAccessToken === AccessTokenStatus.LOGGED_IN
      )
        return;
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

      console.log('message', message);
      console.log('messageStr', JSON.stringify(message.prepareMessage()));

      setMessage(message);

      const msgPrepared = message.prepareMessage();
      // Prompt for signature
      const signResult = await signMessageAsync({
        message: msgPrepared,
      });
      try {
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
      {isConnected && statusAccessToken === AccessTokenStatus.LOGGED_IN && (
        <div className='flex flex-col items-center justify-center h-full text-white'>
          <div className='text-2xl font-bold'>Welcome</div>
          <>
            {botTokens && (
              <>
                <div className='text-1xl font-bold'>Your balance</div>
                <div className='text-xl'>$BOT:{formatEther(botTokens)}</div>
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
