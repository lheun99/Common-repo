/**
 * 빈 목록 안내 (조회 결과가 없을 때 안내 문구와 선택 버튼을 표시)
 *
 * 사용 예: <EmptyState title="주문 없음" message="조회된 주문이 없습니다." actionLabel="조건 초기화" onAction={resetFilter} />
 * 주의: actionLabel과 onAction을 둘 다 넘겨야 버튼이 표시된다.
 */
interface EmptyStateProps {
  /** 굵게 표시할 제목 (선택) */
  title?: string;
  /** 안내 문구 */
  message: string;
  /** 버튼에 표시할 문구 (선택) */
  actionLabel?: string;
  /** 버튼을 눌렀을 때 호출 */
  onAction?: () => void;
}

export function EmptyState({ title, message, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="empty-state" role="status">
      {title && <strong className="empty-state-title">{title}</strong>}
      <p className="empty-state-message">{message}</p>
      {actionLabel && onAction && (
        <button type="button" className="empty-state-action" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}
