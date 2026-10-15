import { addToast, removeToast } from "./toastStore";

// 토스트 알림을 띄우는 hook
export function useToast() {
  return {
    info: (message: string) => addToast("info", message),
    success: (message: string) => addToast("success", message),
    error: (message: string) => addToast("error", message),
    close: (id: number) => removeToast(id),
  };
}
