/**
 * 체크박스 (라벨 클릭으로도 선택 가능)
 *
 * 사용 예: <Checkbox label="약관에 동의합니다" checked={agree} onChange={setAgree} />
 * 주의: 필수 동의 항목은 required를 켜면 라벨 옆에 * 표시가 붙는다.
 */
interface CheckboxProps {
  /** 체크박스 옆에 표시할 문구 */
  label: string;
  /** 선택 여부 */
  checked: boolean;
  /** 선택 상태가 바뀔 때 호출 (바뀐 값 전달) */
  onChange: (checked: boolean) => void;
  /** 비활성화 여부 (기본 false) */
  disabled?: boolean;
  /** 필수 항목 표시 여부 (기본 false) */
  required?: boolean;
}

export function Checkbox({ label, checked, onChange, disabled = false, required = false }: CheckboxProps) {
  return (
    <label className={`checkbox${disabled ? " checkbox-disabled" : ""}`}>
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span>
        {label}
        {required && <span className="checkbox-required">*</span>}
      </span>
    </label>
  );
}
