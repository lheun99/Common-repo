interface InputProps {
  label: string;
  value: string;
  placeholder?: string;
  errorMessage?: string;
  onChange?: (value: string) => void;
}

export function Input({ label, value, placeholder, errorMessage, onChange }: InputProps) {
  return (
    <div className="field">
      <label>{label}</label>
      <input
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange?.(e.target.value)}
      />
      {errorMessage && <span className="error">{errorMessage}</span>}
    </div>
  );
}
