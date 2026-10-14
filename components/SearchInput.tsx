// 검색어 입력창 (목록 화면 상단 검색용)
interface SearchInputProps {
  value: string;
  // 입력할 때마다 호출 (입력된 문자열 전달)
  onChange: (value: string) => void;
  // 검색 실행 시 호출 (앞뒤 공백을 제거한 검색어 전달)
  onSearch: (keyword: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export function SearchInput({
  value,
  onChange,
  onSearch,
  placeholder = "검색어를 입력하세요",
  disabled = false,
}: SearchInputProps) {
  const search = () => {
    const keyword = value.trim();
    if (keyword.length === 0) return;
    onSearch(keyword);
  };

  return (
    <div className="search-input">
      <input
        type="text"
        value={value}
        placeholder={placeholder}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") search();
        }}
      />
      {value.length > 0 && !disabled && (
        <button type="button" onClick={() => onChange("")}>
          지우기
        </button>
      )}
      <button type="button" disabled={disabled} onClick={search}>
        검색
      </button>
    </div>
  );
}
