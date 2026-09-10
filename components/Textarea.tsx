// 여러 줄 텍스트 입력 (라벨/에러 메시지 포함)
interface TextareaProps {
  label: string;
  value: string;
  placeholder?: string;
  errorMessage?: string;
  rows?: number;
  onChange?: (value: string) => void;
}

export function Textarea({ label, value, placeholder, errorMessage, rows = 4, onChange }: TextareaProps) {
  return (
    <div className="field">
      <label>{label}</label>
      <textarea
        value={value}
        placeholder={placeholder}
        rows={rows}
        onChange={(e) => onChange?.(e.target.value)}
      />
      {errorMessage && <span className="error">{errorMessage}</span>}
    </div>
  );
}
