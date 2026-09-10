interface FileUploadProps {
  label: string;
  accept?: string;
  errorMessage?: string;
  onChange: (file: File | null) => void;
}

export function FileUpload({ label, accept, errorMessage, onChange }: FileUploadProps) {
  return (
    <div className="field">
      <label>{label}</label>
      <input
        type="file"
        accept={accept}
        onChange={(e) => onChange(e.target.files?.[0] ?? null)}
      />
      {errorMessage && <span className="error">{errorMessage}</span>}
    </div>
  );
}
