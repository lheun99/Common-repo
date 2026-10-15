import { useEffect, useState } from "react";
import { removeToast, subscribe, type ToastItem } from "./toastStore";

// 화면 오른쪽 위에 토스트 알림을 표시하는 영역. 앱 최상위에 한 번만 넣는다.
export function ToastContainer() {
  const [items, setItems] = useState<ToastItem[]>([]);

  useEffect(() => subscribe(setItems), []);

  return (
    <div className="toast-container">
      {items.map((toast) => (
        <div
          key={toast.id}
          className={`toast toast-${toast.type}`}
          role={toast.type === "error" ? "alert" : "status"}
        >
          <span>{toast.message}</span>
          <button type="button" onClick={() => removeToast(toast.id)}>
            닫기
          </button>
        </div>
      ))}
    </div>
  );
}
