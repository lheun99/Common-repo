/**
 * 탭 메뉴 (한 화면 안에서 여러 영역을 탭으로 전환)
 *
 * 상세 화면처럼 정보가 많은 페이지에서 "기본 정보 / 이력 / 첨부파일"처럼 영역을 나눌 때 사용한다.
 * 선택 상태는 부모가 관리한다 (activeKey + onChange). 탭 내용은 선택된 탭만 렌더링한다.
 *
 * 사용 예:
 *   <Tabs
 *     items={[{ key: "info", label: "기본 정보" }, { key: "history", label: "이력", badge: 3 }]}
 *     activeKey={tab}
 *     onChange={setTab}
 *   />
 *
 * 주의: items의 key는 화면 안에서 중복되면 안 된다.
 * 주의: disabled 탭은 클릭해도 onChange가 호출되지 않는다.
 */
interface TabItem {
  /** 탭 식별값 (activeKey와 비교) */
  key: string;
  /** 탭에 표시할 이름 */
  label: string;
  /** 이름 옆에 표시할 숫자 (0이면 표시 안 함) */
  badge?: number;
  /** true면 선택할 수 없음 */
  disabled?: boolean;
}

interface TabsProps {
  /** 탭 목록 (표시 순서대로) */
  items: TabItem[];
  /** 현재 선택된 탭의 key */
  activeKey: string;
  /** 탭을 눌렀을 때 호출 (선택된 key 전달) */
  onChange: (key: string) => void;
  /** 탭 바를 화면 너비에 꽉 채울지 여부 (기본 false) */
  fullWidth?: boolean;
}

export function Tabs({ items, activeKey, onChange, fullWidth = false }: TabsProps) {
  return (
    <div className={`tabs${fullWidth ? " tabs-full" : ""}`} role="tablist">
      {items.map((item) => (
        <button
          key={item.key}
          type="button"
          role="tab"
          aria-selected={item.key === activeKey}
          className={`tab${item.key === activeKey ? " tab-active" : ""}`}
          disabled={item.disabled}
          onClick={() => !item.disabled && onChange(item.key)}
        >
          {item.label}
          {item.badge ? <span className="tab-badge">{item.badge}</span> : null}
        </button>
      ))}
    </div>
  );
}
