import { useMemo, useState } from 'react';
import { CommonInputProps, InputBase } from '.';

export const EtherInput = ({
  value,
  name,
  placeholder,
  onChange,
}: CommonInputProps) => {
  const [transitoryValue, setTransitoryValue] = useState<string | undefined>();

  const displayValue = useMemo(() => {
    let newValue = value;

    if (transitoryValue) {
      newValue = transitoryValue;
      setTransitoryValue(undefined);
    }

    return newValue;
  }, [value, transitoryValue]);

  const handleChangeNumber = (newValue: string) => {
    if (typeof newValue === 'string') {
      if (newValue.endsWith('.') || newValue.endsWith('.0')) {
        setTransitoryValue(newValue);
      } else {
        setTransitoryValue(undefined);
        // newValue = parseEther(newValue as `${number}`);
      }
      onChange(newValue);
    }
  };

  return (
    <InputBase
      name={name}
      value={displayValue}
      placeholder={placeholder}
      onChange={handleChangeNumber}
      prefix={
        <span className='pl-4 -mr-2 text-accent self-center text-gray-400'>
          {'Ξ'}
        </span>
      }
    />
  );
};
