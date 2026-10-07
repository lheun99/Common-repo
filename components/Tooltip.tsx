/**
 * 툴팁 (마우스를 올리면 설명 문구 표시)
 *
 * 사용 예: <Tooltip text="삭제하면 복구할 수 없습니다"><Button label="삭제" variant="danger" /></Tooltip>
 * 주의: text가 길면 maxWidth로 줄바꿈 폭을 지정한다.
 */
interface TooltipProps {
  /** 표시할 설명 문구 */
  text: string;
  /** 툴팁 위치 (기본 top) */
  position?: "top" | "bottom" | "left" | "right";
  /** 줄바꿈 기준 최대 너비(px) */
  maxWidth?: number;
  children: React.ReactNode;
}

export function Tooltip({ text, position = "top", maxWidth = 240, children }: TooltipProps) {
  return (
    <span className={`tooltip tooltip-${position}`} data-tooltip={text} style={{ maxWidth }}>
      {children}
    </span>
  );
}
