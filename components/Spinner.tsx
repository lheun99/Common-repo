/**
 * 로딩 스피너 (데이터를 불러오거나 저장하는 동안 진행 중임을 표시)
 *
 * 사용 예: <Spinner size="large" label="목록을 불러오는 중..." />
 * 주의: 버튼 안에 넣을 때는 size="small"을 쓰고 label은 생략한다.
 */
interface SpinnerProps {
  /** 스피너 크기 (기본 medium) */
  size?: "small" | "medium" | "large";
  /** 스피너 옆에 표시할 안내 문구 (선택) */
  label?: string;
  /** true면 화면 전체를 덮는 반투명 배경 위에 표시 */
  overlay?: boolean;
}

export function Spinner({ size = "medium", label, overlay = false }: SpinnerProps) {
  const spinner = (
    <div className={`spinner spinner-${size}`} role="status" aria-live="polite">
      <span className="spinner-circle" aria-hidden="true" />
      <span className={label ? "spinner-label" : "sr-only"}>{label ?? "로딩 중"}</span>
    </div>
  );

  return overlay ? <div className="spinner-overlay">{spinner}</div> : spinner;
}
