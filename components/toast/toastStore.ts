export type ToastType = "info" | "success" | "error";

export interface ToastItem {
  id: number;
  type: ToastType;
  message: string;
}

const MAX_TOASTS = 3;
const DURATION_MS = 3000;

let toasts: ToastItem[] = [];
let nextId = 1;
const listeners = new Set<(items: ToastItem[]) => void>();

function emit() {
  listeners.forEach((listener) => listener(toasts));
}

export function subscribe(listener: (items: ToastItem[]) => void) {
  listeners.add(listener);
  listener(toasts);
  return () => {
    listeners.delete(listener);
  };
}

export function addToast(type: ToastType, message: string) {
  const id = nextId++;
  toasts = [...toasts, { id, type, message }].slice(-MAX_TOASTS);
  emit();

  if (type !== "error") {
    setTimeout(() => removeToast(id), DURATION_MS);
  }
  return id;
}

export function removeToast(id: number) {
  toasts = toasts.filter((toast) => toast.id !== id);
  emit();
}
