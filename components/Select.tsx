interface SelectOption {
  label: string;
  value: string;
}

interface SelectProps {
  label: string;
  value: string;
  options: SelectOption[];
  errorMessage?: string;
  onChange?: (value: string) => void;
}

export function Select({ label, value, options, errorMessage, onChange }: SelectProps) {
  return (
    <div className="field">
      <label>{label}</label>
      <select value={value} onChange={(e) => onChange?.(e.target.value)}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {errorMessage && <span className="error">{errorMessage}</span>}
    </div>
  );
}
