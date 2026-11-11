// 목록 하단 페이지 넘기기
interface PaginationProps {
  page: number;
  totalPages: number;
  pageSize?: number;
  onChange: (value: { page: number; pageSize: number }) => void;
}

export function Pagination({ page, totalPages, pageSize = 20, onChange }: PaginationProps) {
  return (
    <div className="pagination">
      <button disabled={page <= 1} onClick={() => onChange({ page: page - 1, pageSize })}>
        이전
      </button>
      <span>
        {page} / {totalPages}
      </span>
      <button disabled={page >= totalPages} onClick={() => onChange({ page: page + 1, pageSize })}>
        다음
      </button>
    </div>
  );
}
