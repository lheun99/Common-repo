/**
 * 알림 메시지 박스 (안내·성공·경고·오류 문구를 화면 상단이나 폼 위에 표시)
 *
 * 사용 예: <Alert variant="error" title="저장 실패" message="잠시 후 다시 시도해 주세요." onClose={hideAlert} />
 * 주의: onClose를 넘기지 않으면 닫기 버튼이 표시되지 않는다.
 */
interface AlertProps {
  /** 본문 문구 */
  message: string;
  /** 알림 종류 (기본 info) */
  variant?: "info" | "success" | "warning" | "error";
  /** 굵게 표시할 제목 (선택) */
  title?: string;
  /** 닫기 버튼을 눌렀을 때 호출 */
  onClose?: () => void;
}

export function Alert({ message, variant = "info", title, onClose }: AlertProps) {
  return (
    <div className={`alert alert-${variant}`} role={variant === "error" ? "alert" : "status"}>
      <div className="alert-body">
        {title && <strong className="alert-title">{title}</strong>}
        <span>{message}</span>
      </div>
      {onClose && (
        <button type="button" className="alert-close" aria-label="닫기" onClick={onClose}>
          ×
        </button>
      )}
    </div>
  );
}
